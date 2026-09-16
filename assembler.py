import sys
from pathlib import Path

from parser import Parser
from code import dest, comp, jump
from symbol_table import SymbolTable


def first_pass(lines, symbol_table):

    parser = Parser(lines)
    rom_address = 0

    while parser.has_more_commands():

        parser.advance()

        if parser.command_type() == "L_COMMAND":

            symbol = parser.symbol()

            if not symbol_table.contains(symbol):
                symbol_table.add(symbol, rom_address)

        else:
            rom_address += 1


def second_pass(lines, symbol_table):

    parser = Parser(lines)

    output = []
    next_variable_address = 16

    while parser.has_more_commands():

        parser.advance()

        command_type = parser.command_type()

        # -------------------------
        # A-INSTRUCTION
        # -------------------------

        if command_type == "A_COMMAND":

            symbol = parser.symbol()

            if symbol.isdigit():

                address = int(symbol)

            else:

                if not symbol_table.contains(symbol):

                    symbol_table.add(
                        symbol,
                        next_variable_address
                    )

                    next_variable_address += 1

                address = symbol_table.get_address(symbol)

            binary = format(address, "016b")

            output.append(binary)

        # -------------------------
        # LABEL
        # -------------------------

        elif command_type == "L_COMMAND":

            continue

        # -------------------------
        # C-INSTRUCTION
        # -------------------------

        elif command_type == "C_COMMAND":

            dest_bits = dest(parser.dest())
            comp_bits = comp(parser.comp())
            jump_bits = jump(parser.jump())

            binary = (
                "111"
                + comp_bits
                + dest_bits
                + jump_bits
            )

            output.append(binary)

    return output


def assemble(input_file, output_file):

    # Read ASM file
    with open(input_file, "r") as file:
        lines = file.readlines()

    print("Input file:")
    print(input_file)

    # Create symbol table
    symbol_table = SymbolTable()

    # Pass 1
    print("Pass 1: Finding labels...")
    first_pass(lines, symbol_table)

    # Pass 2
    print("Pass 2: Generating binary...")
    machine_code = second_pass(lines, symbol_table)

    # Write .hack file
    with open(output_file, "w") as file:

        for instruction in machine_code:
            file.write(instruction + "\n")

    print()
    print("Assembly successful!")
    print("Output file:")
    print(output_file)
    print("Instructions:", len(machine_code))

    # Show binary
    print()
    print("Generated binary:")
    print("-----------------")

    for instruction in machine_code:
        print(instruction)


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python assembler.py Add.asm")
        return

    input_file = Path(sys.argv[1])

    if not input_file.exists():

        print("ERROR: File does not exist")
        print(input_file)
        return

    output_file = input_file.with_suffix(".hack")

    try:
        assemble(
            input_file,
            output_file
        )

    except Exception as error:

        print()
        print("ASSEMBLER ERROR:")
        print(error)


if __name__ == "__main__":
    main()