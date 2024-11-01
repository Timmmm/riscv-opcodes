import collections
import glob
import logging
import os
import pprint
import re
import sys

import yaml

# from shared_utils import overlaps, overlap_allowed, extension_overlap_allowed, instruction_overlap_allowed, process_enc_line, same_base_isa, add_segmented_vls_insn, expand_nf_field
from shared_utils import *

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:: %(message)s")


def make_sverilog(instr_dict):
    names_str = ""
    for i in instr_dict:
        names_str += f"  localparam [31:0] {i.upper().replace('.','_'):<18s} = 32'b{instr_dict[i]['encoding'].replace('-','?')};\n"
    names_str += "  /* CSR Addresses */\n"
    for num, name in csrs + csrs32:
        names_str += (
            f"  localparam logic [11:0] CSR_{name.upper()} = 12'h{hex(num)[2:]};\n"
        )

    sverilog_file = open("inst.sverilog", "w")
    sverilog_file.write(
        f"""
/* Automatically generated by parse_opcodes */
package riscv_instr;
{names_str}
endpackage
"""
    )
    sverilog_file.close()
