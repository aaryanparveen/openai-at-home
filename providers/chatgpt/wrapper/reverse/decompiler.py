import re
import json
import base64


class Decompiler:
    
    
    mapping: dict = {
        "1": "XOR_STR",
        "2": "SET_VALUE",
        "3": "BTOA",
        "4": "BTOA_2",
        "5": "ADD_OR_PUSH",
        "6": "ARRAY_ACCESS",
        "7": "CALL",
        "8": "COPY",
        "10": "window",
        "11": "GET_SCRIPT_SRC",
        "12": "GET_MAP",
        "13": "TRY_CALL",
        "14": "JSON_PARSE",
        "15": "JSON_STRINGIFY",
        "17": "CALL_AND_SET",
        "18": "ATOB",
        "19": "BTOA_3",
        "20": "IF_EQUAL_CALL",
        "21": "IF_DIFF_CALL",
        "22": "TEMP_STACK_CALL",
        "23": "IF_DEFINED_CALL",
        "24": "BIND_METHOD",
        "27": "REMOVE_OR_SUBTRACT",
        "28": "undefined",
        "25": "undefined",
        "26": "undefined",
        "29": "LESS_THAN",
        "31": "INCREMENT",
        "32": "DECREMENT_AND_EXEC",
        "33": "MULTIPLY",
        "34": "MOVE"
    }

    functions: dict = {
            "XOR_STR": """function XOR_STR(e, t) {
        e = String(e);
        t = String(t);
        let n = "";
        for (let r = 0; r < e.length; r++)
            n += String.fromCharCode(e.charCodeAt(r) ^ t.charCodeAt(r % t.length));
        return n;
    }
