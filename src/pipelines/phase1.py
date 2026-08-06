from __future__ import annotations
from datetime import datetime, UTC


def main() -> None:
    """TODO(student): xay dung baseline pipeline end-to-end.

    run_date = datetime.now(UTC)
    df = build_clean_dataframe(
        records=records,
        run_date=run_date
    )
    
    # Save the dataframe since cleaning.py no longer does it
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.paths.clean_csv, index=False)
    df.to_json(settings.paths.clean_json, orient='records', force_ascii=False, indent=4)6. Tao hoac load evaluation set.
    7. Evaluate.
    8. Run quality checks va freshness report.
    9. Tao markdown report.
    10. Co the demo agent tren vai sample question.
    """
    raise NotImplementedError("Student task: implement phase1 pipeline.")
