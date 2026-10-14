from fastapi import APIRouter, HTTPException

from src.memory.execution_context import execution_context


router = APIRouter()


@router.get(
    "/observability/{execution_id}",
)
def get_observability(
    execution_id: str,
):
    """
    Return observability information for the current execution.
    """

    runtime = execution_context.get()

    # ---------------------------------------------------------
    # Validate Execution ID
    # ---------------------------------------------------------

    if runtime.id != execution_id:

        raise HTTPException(
            status_code=404,
            detail="Execution not found.",
        )

    # ---------------------------------------------------------
    # Return Observability Data
    # ---------------------------------------------------------

    return execution_context.to_dict()