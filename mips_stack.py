# IDA plugin to name stack variables that are simply used to store register
# values until a function returns ($ra, $s0-$s7, $fp, $gp).
#
# Invoke by going to Plugins->Mips saved registers renamer,
# or by pressing Alt + Shift + 2.
#
# Craig Heffner
# Tactical Network Solutions

import idaapi
import idautils
import idc
import ida_auto

class NameMIPSSavedRegisters(object):
	INSIZE = 4
	SEARCH_DEPTH = 35

	ARCH = {
			'savedregs': ['$s0', '$s1', '$s2', '$s3', '$s4', '$s5', '$s6',
						  '$s7', '$fp', '$gp', '$ra', '$f20', '$f21', '$f22',
						  '$f23', '$f24', '$f25', '$f26', '$f27', '$f28', '$f29', '$f30', '$f31'],
	}

	def __init__(self):
		print("Naming saved register locations...", end=' ')

		for ea in idautils.Functions():
			mea = ea
			named_regs = []
			last_iteration = False

			while mea < (ea + (self.INSIZE * self.SEARCH_DEPTH)):
				mnem = idc.print_insn_mnem(mea)

				if mnem in ['sw', 'sd', 'sq', 'swc1', 'sdc1']:
					reg = idc.print_operand(mea, 0)
					dst = idc.print_operand(mea, 1)

					if reg in self.ARCH['savedregs'] and \
							reg not in named_regs and \
							dst.endswith('($sp)') and 'var_' in dst:
						split_string = 'var_'
						stack_position = "[sp-%d]"
						if '_s' in dst:
							split_string += 's'
							stack_position = "[sp+%d]"

						offset = int(dst.split(split_string)[1].split('(')[0],
									 16)
						idc.define_local_var(
							ea, idc.find_func_end(ea),
							stack_position % offset, "saved_%s" % reg[1:])
						named_regs.append(reg)

				if last_iteration:
					break
				elif mnem.startswith('j') or mnem.startswith('b'):
					last_iteration = True

				mea += self.INSIZE

		print("Mips saved registers renamer done.")

def name_saved_registers():
	NameMIPSSavedRegisters()

class mips_saved_registers_t(idaapi.plugin_t):
	flags = 0
	comment = "Renames MIPS registers saved on the stack"
	help = "Renames MIPS registers saved on the stack"
	wanted_name = "Mips saved registers renamer"
	wanted_hotkey = "Alt-Shift-2"
	
	def init(self):
		if (idaapi.ph.id == idaapi.PLFM_MIPS):
			idaapi.msg("Mips saved registers renamer loaded.\n")
			return idaapi.PLUGIN_KEEP
			
		return idaapi.PLUGIN_SKIP
		
	def run(self, arg):
		if ida_auto.auto_is_ok() == 1:
			name_saved_registers()
		else:
			idaapi.warning("Aborted! Run plugin again after initial autoanalyze finished.")
			
	def term(self):
		pass

def PLUGIN_ENTRY():
	return mips_saved_registers_t()