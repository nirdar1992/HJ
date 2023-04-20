def extract_family_name(drill_name):
    try:
        first_word = drill_name[:drill_name.index(" ")]
    except:
        first_word = drill_name
    if first_word == "ATTACKING" or first_word == "OFFENCE" or drill_name.startswith("SET PIECES"):
        return "OFFENCE"
    elif "VS" in first_word:
        return "INNER GAMES"
    else:
        return first_word
