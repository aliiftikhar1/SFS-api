from Utilities.Enums.BaseEnum import BaseEnum


class KeyScaleTypes(BaseEnum):
    MINOR = "Minor"
    MAJOR = "Major"


class KeyTypes(BaseEnum):
    FLAT = "Flat"
    SHARP = "Sharp"


class FlatKeys(BaseEnum):
    Db = "Db"
    Eb = "Eb"
    Gb = "Gb"
    Ab = "Ab"
    Bb = "Bb"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class SharpKeys(BaseEnum):
    DS = "D#"
    ES = "E#"
    GS = "G#"
    AS = "A#"
    BS = "B#"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
