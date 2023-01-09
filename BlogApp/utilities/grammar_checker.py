from gingerit.gingerit import GingerIt
import pandas as pd

parser = GingerIt()

def correct_text(text):
    return parser.parse(text)


def generate_df(text):
    pd.set_option('max_colwidth', 520)
    corrected_text = pd.DataFrame(correct_text(text))
    table_html = corrected_text.to_html(classes='mystyle')
    return table_html