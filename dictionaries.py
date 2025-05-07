identifierDict = {"Trent 1000": "1000",
                  "Trent 7000": "7000",
                  "Trent 9": "900",
                  "TRENTXWB": "XWB"}

splitterDict = {"1000": r"\]TRENT/ALL|\]SEE EFFECTIVITY SECTION|Filtering is",
                "7000": r"\]TRENT/ALL|\]SEE EFFECTIVITY SECTION|Filtering is",
                "900": r"RevDate:|Filtering is",
                "XWB": r"Number: \d{3}|Filtering is"}

subtaskIdentifierDict = {"1000": "SUBTASK ",
                         "7000": "SUBTASK ",
                         "900": "SUBTASK ",
                         "XWB": "Sub-Procedure "}