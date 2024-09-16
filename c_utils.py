import re
import glob
import os
import pprint
import logging
import collections
import yaml
import sys
# from shared_utils import overlaps, overlap_allowed, extension_overlap_allowed, instruction_overlap_allowed, process_enc_line, same_base_isa, add_segmented_vls_insn, expand_nf_field
from shared_utils import *

pp = pprint.PrettyPrinter(indent=2)
logging.basicConfig(level=logging.INFO, format='%(levelname)s:: %(message)s')

def make_c(instr_dict):
    mask_match_str = ''
    declare_insn_str = ''
    for i in instr_dict:
        mask_match_str += f'#define MATCH_{i.upper().replace(".","_")} {instr_dict[i]["match"]}\n'
        mask_match_str += f'#define MASK_{i.upper().replace(".","_")} {instr_dict[i]["mask"]}\n'
        declare_insn_str += f'DECLARE_INSN({i.replace(".","_")}, MATCH_{i.upper().replace(".","_")}, MASK_{i.upper().replace(".","_")})\n'

    csr_names_str = ''
    declare_csr_str = ''
    for num, name in csrs+csrs32:
        csr_names_str += f'#define CSR_{name.upper()} {hex(num)}\n'
        declare_csr_str += f'DECLARE_CSR({name}, CSR_{name.upper()})\n'

    causes_str= ''
    declare_cause_str = ''
    for num, name in causes:
        causes_str += f"#define CAUSE_{name.upper().replace(' ', '_')} {hex(num)}\n"
        declare_cause_str += f"DECLARE_CAUSE(\"{name}\", CAUSE_{name.upper().replace(' ','_')})\n"

    arg_str = ''
    for name, rng in arg_lut.items():
        begin = rng[1]
        end   = rng[0]
        mask = ((1 << (end - begin + 1)) - 1) << begin
        arg_str += f"#define INSN_FIELD_{name.upper().replace(' ', '_')} {hex(mask)}\n"

    with open(f'{os.path.dirname(__file__)}/encoding.h', 'r') as file:
        enc_header = file.read()

    commit = os.popen('git log -1 --format="format:%h"').read()
    enc_file = open('encoding.out.h','w')
    enc_file.write(f'''/* SPDX-License-Identifier: BSD-3-Clause */

/* Copyright (c) 2023 RISC-V International */

/*
 * This file is auto-generated by running 'make' in
 * https://github.com/riscv/riscv-opcodes ({commit})
 */

{enc_header}
/* Automatically generated by parse_opcodes. */
#ifndef RISCV_ENCODING_H
#define RISCV_ENCODING_H
{mask_match_str}
{csr_names_str}
{causes_str}
{arg_str}#endif
#ifdef DECLARE_INSN
{declare_insn_str}#endif
#ifdef DECLARE_CSR
{declare_csr_str}#endif
#ifdef DECLARE_CAUSE
{declare_cause_str}#endif
''')
    enc_file.close()
