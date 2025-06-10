identifierDict = {"Trent 1000": "1000",
                  "Trent 7000": "7000",
                  "Trent 9": "900",
                  "TRENTXWB": "XWB"}

# if there are errors with splitting into more parts than expected, error is probably here
splitterDict = {"1000": r"\]TRENT/ALL|Effectivity: TRENT/ALL\n|NOT FOR\nMANUFACTURE|Filtering is",
                "7000": r"\]TRENT/ALL|Effectivity: TRENT/ALL\n|NOT FOR\nMANUFACTURE|Filtering is",
                "900": r"RevDate:|Filtering is",
                "XWB": r"Number: \d{3}|Filtering is"}

subtaskIdentifierDict = {"1000": "SUBTASK ",
                         "7000": "SUBTASK ",
                         "900": "SUBTASK ",
                         "XWB": "Sub-Procedure "}

taskEndText = {"1000": "See graphics after the end of section.",
               "7000": "See graphics after the end of section.",
               "900": "See graphics after the end of section.",
               "XWB": "See graphics after the end of section."}

stepIgnoreText = {"1000": [r"^Export Rating.*", r"RevDate:", r"\b\d{2}/[A-Z]{3}/\d{4}\b", r"^Model:.*", "REMOVAL", "INSTALLATION"],
                  "7000": [r"^Export Rating.*", r"RevDate:", r"\b\d{2}/[A-Z]{3}/\d{4}\b", r"^Model:.*", "REMOVAL", "INSTALLATION"],
                  "900": [r"^Export Rating.*", r"RevDate:", r"\b\d{2}/[A-Z]{3}/\d{4}\b", r"^Model:.*", "REMOVAL", "INSTALLATION"],
                  "XWB": []}