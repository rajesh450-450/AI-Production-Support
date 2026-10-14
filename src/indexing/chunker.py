from __future__ import annotations

import re

from src.indexing.models import SourceDocument
from src.indexing.models import (
    DocumentChunk,
    SourceDocument,
)


class DocumentChunker:
    """
    Structure-aware document chunker.

    Goals:
    - Preserve semantic boundaries where possible.
    - Maximum chunk size <= chunk_size.
    - Target overlap approximately chunk_overlap.
    - Prefer clean overlap boundaries.
    - Avoid tiny chunks caused by overlap.
    - Avoid splitting words.
    - Prefer sentence/paragraph boundaries.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        minimum_new_content: int = 300,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        if minimum_new_content <= 0:
            raise ValueError(
                "minimum_new_content must be greater than zero."
            )

        if minimum_new_content > chunk_size - chunk_overlap:
            raise ValueError(
                "minimum_new_content is too large for "
                "the configured chunk size and overlap."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.minimum_new_content = minimum_new_content

    # ================================================================
    # PUBLIC API
    # ================================================================

    def chunk_document(
        self,
        document: SourceDocument,
    ) -> list[DocumentChunk]:

        text = self._normalize_text(document.text)

        if not text:
            return []

        blocks = self._extract_blocks(text)

        if not blocks:
            return []

        chunk_texts = self._build_chunks(blocks)

        return [
            DocumentChunk(
                chunk_id=(
                    f"{document.document_id}"
                    f"-chunk-{index:04d}"
                ),
                document_id=document.document_id,
                source=document.source,
                external_id=document.external_id,
                title=document.title,
                text=chunk_text,
                chunk_index=index,
                metadata=dict(document.metadata),
            )
            for index, chunk_text in enumerate(chunk_texts)
        ]

    def chunk_documents(
        self,
        documents: list[SourceDocument],
    ) -> list[DocumentChunk]:

        result: list[DocumentChunk] = []

        for document in documents:
            result.extend(
                self.chunk_document(document)
            )

        return result

    # ================================================================
    # TEXT NORMALIZATION
    # ================================================================

    @staticmethod
    def _normalize_text(text: str) -> str:

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = [
            line.rstrip()
            for line in text.split("\n")
        ]

        text = "\n".join(lines)

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # ================================================================
    # STRUCTURE EXTRACTION
    # ================================================================

    @staticmethod
    def _extract_blocks(
        text: str,
    ) -> list[str]:

        raw_blocks = re.split(
            r"\n\s*\n",
            text,
        )

        blocks: list[str] = []

        for block in raw_blocks:

            block = block.strip()

            if not block:
                continue

            lines = [
                line.strip()
                for line in block.split("\n")
                if line.strip()
            ]

            if lines:
                blocks.append(
                    "\n".join(lines)
                )

        return blocks

    # ================================================================
    # MAIN CHUNKING ALGORITHM
    # ================================================================

    def _build_chunks(
        self,
        blocks: list[str],
    ) -> list[str]:

        chunks: list[str] = []

        current = ""

        index = 0

        while index < len(blocks):

            block = blocks[index]

            # --------------------------------------------------------
            # Oversized block
            # --------------------------------------------------------

            if len(block) > self.chunk_size:

                if current:
                    chunks.append(current)
                    current = ""

                pieces = self._split_large_block(
                    block
                )

                chunks.extend(
                    self._apply_overlap_to_pieces(
                        pieces
                    )
                )

                index += 1
                continue

            # --------------------------------------------------------
            # Start first chunk
            # --------------------------------------------------------

            if not current:

                current = block
                index += 1
                continue

            # --------------------------------------------------------
            # Try adding next semantic block
            # --------------------------------------------------------

            candidate = (
                current
                + "\n\n"
                + block
            )

            if len(candidate) <= self.chunk_size:

                current = candidate
                index += 1
                continue

            # --------------------------------------------------------
            # Current chunk is full enough.
            # Finalize it.
            # --------------------------------------------------------

            chunks.append(current)

            overlap = self._get_overlap(
                current
            )

            available = (
                self.chunk_size
                - len(overlap)
                - 2
            )

            if available <= 0:
                raise RuntimeError(
                    "No room remains for new content "
                    "after applying overlap."
                )

            # --------------------------------------------------------
            # If next block is too large to fit after overlap,
            # split it intelligently.
            # --------------------------------------------------------

            if len(block) > available:

                pieces = self._split_to_size(
                    block,
                    available,
                )

                current = (
                    overlap
                    + "\n\n"
                    + pieces[0]
                )

                blocks[index:index + 1] = pieces[1:]

                index += 1
                continue

            # --------------------------------------------------------
            # Normal next chunk.
            # --------------------------------------------------------

            current = (
                overlap
                + "\n\n"
                + block
            )

            index += 1

        if current:
            chunks.append(current)

        # ------------------------------------------------------------
        # Final balancing pass.
        # ------------------------------------------------------------

        chunks = self._rebalance_small_tail_chunks(
            chunks
        )

        return chunks

    # ================================================================
    # LARGE BLOCK SPLITTING
    # ================================================================

    def _split_large_block(
        self,
        block: str,
    ) -> list[str]:

        if len(block) <= self.chunk_size:
            return [block]

        return self._split_to_size(
            block,
            self.chunk_size,
        )

    def _split_to_size(
        self,
        text: str,
        max_size: int,
    ) -> list[str]:

        pieces: list[str] = []

        remaining = text.strip()

        while len(remaining) > max_size:

            candidate = remaining[:max_size]

            split_position = (
                self._find_best_split_position(
                    candidate
                )
            )

            piece = (
                remaining[:split_position]
                .strip()
            )

            if not piece:
                split_position = max_size
                piece = remaining[:split_position]

            pieces.append(piece)

            remaining = (
                remaining[split_position:]
                .strip()
            )

        if remaining:
            pieces.append(remaining)

        return pieces

    @staticmethod
    def _find_best_split_position(
        text: str,
    ) -> int:

        # Prefer sentence boundary.
        matches = list(
            re.finditer(
                r"[.!?](?:\s|$)",
                text,
            )
        )

        if matches:

            position = matches[-1].end()

            if position >= int(
                len(text) * 0.60
            ):
                return position

        # Then paragraph/line boundary.
        newline = text.rfind("\n")

        if newline >= int(len(text) * 0.60):
            return newline

        # Then word boundary.
        whitespace = text.rfind(" ")

        if whitespace >= int(len(text) * 0.60):
            return whitespace

        # Last resort.
        return len(text)

    # ================================================================
    # OVERLAP
    # ================================================================

    def _get_overlap(
        self,
        text: str,
    ) -> str:
        """
        Return an overlap from the end of the previous chunk.

        The important difference from the previous implementation is
        that we do NOT blindly take the final N characters.

        We first locate an approximate overlap window and then move
        its beginning to a clean semantic boundary.

        Priority:
        1. Paragraph boundary
        2. Line boundary
        3. Sentence boundary
        4. Word boundary
        5. Character boundary as final fallback

        The resulting overlap may therefore be slightly smaller than
        chunk_overlap. This is intentional: clean semantic boundaries
        are more important than blindly preserving an exact character
        count.
        """

        if not text:
            return ""

        if len(text) <= self.chunk_overlap:
            return text

        target_start = (
            len(text) - self.chunk_overlap
        )

        # ------------------------------------------------------------
        # 1. Prefer paragraph boundary.
        #
        # We look for the closest "\n\n" before the target.
        # ------------------------------------------------------------

        paragraph_positions = [
            match.start() + 2
            for match in re.finditer(
                r"\n\n",
                text[:target_start],
            )
        ]

        if paragraph_positions:

            position = paragraph_positions[-1]

            if position >= int(
                target_start * 0.70
            ):
                return text[position:].strip()

        # ------------------------------------------------------------
        # 2. Prefer line boundary.
        # ------------------------------------------------------------

        newline = text.rfind(
            "\n",
            0,
            target_start,
        )

        if newline != -1:

            position = newline + 1

            if position >= int(
                target_start * 0.70
            ):
                return text[position:].strip()

        # ------------------------------------------------------------
        # 3. Prefer sentence boundary.
        #
        # Search for the last sentence ending before target_start.
        # ------------------------------------------------------------

        sentence_matches = list(
            re.finditer(
                r"[.!?](?:\s|$)",
                text[:target_start],
            )
        )

        if sentence_matches:

            position = sentence_matches[-1].end()

            if position >= int(
                target_start * 0.70
            ):
                return text[position:].strip()

        # ------------------------------------------------------------
        # 4. Prefer word boundary.
        # ------------------------------------------------------------

        whitespace = text.rfind(
            " ",
            0,
            target_start,
        )

        if whitespace != -1:

            position = whitespace + 1

            if position >= int(
                target_start * 0.70
            ):
                return text[position:].strip()

        # ------------------------------------------------------------
        # 5. Final fallback.
        #
        # This should be rare. It preserves the original behavior
        # when no reasonable boundary exists.
        # ------------------------------------------------------------

        return text[
            -self.chunk_overlap:
        ].strip()

    # ================================================================
    # OVERLAP FOR OVERSIZED BLOCKS
    # ================================================================

    def _apply_overlap_to_pieces(
        self,
        pieces: list[str],
    ) -> list[str]:

        if not pieces:
            return []

        result = [pieces[0]]

        for piece in pieces[1:]:

            previous = result[-1]

            overlap = self._get_overlap(
                previous
            )

            available = (
                self.chunk_size
                - len(overlap)
                - 2
            )

            if len(piece) <= available:

                result.append(
                    overlap
                    + "\n\n"
                    + piece
                )

            else:

                subpieces = self._split_to_size(
                    piece,
                    available,
                )

                for subpiece in subpieces:

                    previous = result[-1]

                    overlap = self._get_overlap(
                        previous
                    )

                    result.append(
                        overlap
                        + "\n\n"
                        + subpiece
                    )

        return result

    # ================================================================
    # SMALL TAIL REBALANCING
    # ================================================================

    def _rebalance_small_tail_chunks(
        self,
        chunks: list[str],
    ) -> list[str]:

        if len(chunks) < 2:
            return chunks

        result = list(chunks)

        last = result[-1]
        previous = result[-2]

        overlap = self._get_overlap(
            previous
        )

        new_content_length = (
            len(last)
            - len(overlap)
            - 2
        )

        if (
            new_content_length
            >= self.minimum_new_content
        ):
            return result

        new_content = last[
            len(overlap):
        ].lstrip()

        merged = (
            previous
            + "\n\n"
            + new_content
        )

        if len(merged) <= self.chunk_size:

            result[-2] = merged
            result.pop()

        return result

    # ================================================================
    # UTILITY
    # ================================================================

    @staticmethod
    def _is_heading(
        text: str,
    ) -> bool:

        first_line = text.split(
            "\n",
            1,
        )[0].strip()

        return bool(
            re.match(
                r"^\d+[\.\)]\s+.+$",
                first_line,
            )
        )