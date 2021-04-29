
def validate_exp_date(days_to_live):
    try:
        days_to_live = int(days_to_live)
        if days_to_live > 365*3:
            days_to_live = 365*3
        if days_to_live < 0:
            print("Negative integer is not allowed")
            raise Exception
        days_to_live = str(days_to_live)
    except Exception as error:
        print(error)
        days_to_live = None
    return days_to_live


def validate_suffix(suffix):
    if suffix:
        suffix = suffix.strip()
        suffix = suffix.replace(" ", "_")
    return suffix