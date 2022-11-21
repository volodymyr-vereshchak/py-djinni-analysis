import pandas as pd
import matplotlib.pyplot as plot


def analyse(file_name: str, exp: int) -> None:
    df = pd.read_csv(file_name)
    if exp:
        title = f"Analyse technologies with experience = {exp}"
        df[df["experience"] == exp]["technologies"].value_counts().head(20).plot(
            kind="bar", title=title
        )
    else:
        title = "Analyse technologies"
        df["technologies"].value_counts().head(20).plot(kind="bar", title=title)
    plot.tight_layout()
    plot.show()


def compare_analyse(file_name_1: str, file_name_2: str, exp: int) -> None:
    if exp:
        df1 = pd.read_csv(file_name_1)
        df1 = df1[df1["experience"] == exp]["technologies"].value_counts()
        df2 = pd.read_csv(file_name_2)
        df2 = df2[df2["experience"] == exp]["technologies"].value_counts()
        title = f"Analyse technologies with experience = {exp}"
    else:
        df1 = pd.read_csv(file_name_1)["technologies"].value_counts()
        df2 = pd.read_csv(file_name_2)["technologies"].value_counts()
        title = "Analyse technologies"

    (df2 - df1).head(20).plot(kind="bar", title=title)
    plot.tight_layout()
    plot.show()
