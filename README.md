# Tomasulo
   

### Parameters
Change the number of register/instruction buffer size/number of reservation station for each functional unit using **Parameters.txt** file.

**Default Values**
```
number_of_registers: 32
instruction_window_size: 4
fp_mul_RS_size: 2
fp_add_RS_size: 3
int_add_RS_size: 4
```

The length of ROB defaults to 64, but can be changed at the location of the main.py **ROB = ReorderBuffer(64)**.

Also, the length of LoadStoreQueue can also be changed(defaults to 10) at the location of the FunctionalUnit.py **lsq_size = 10**.

Modifying the cycles of Load/Store in memory is a little tricky. It requires searching for all cyclesMemRemained in Tomasulo.py such that cyclesMemRemained equals to the desired number. **Default is 4.**
If I change the way to modify the value, I will update this section.

### Functional Units
Functional units can be configured using **Units.txt** file. The number at the end of each row indicated the cycles it requires at the EX stage.

**Default Values**
```
0: Add,Addi,Sub,Bne,Beq 1   # interger adder
1: Add.d,Sub.d 4            # floating point adder
2: Mult.d,Div 15            # floating point multiplier
3: Ld,Sd 1
```

### The program
Put the to execute in **Program.txt**.

The program should be in the following format:
```
Add     R0, R1, R2
Addi    R1, R2, 1
Sub     R2, R1, 1
Add.d   F0, F1, F2
Sub.d   F1, F2, F3
Mult.d  F2, F1, F0
Div     F3, F2, F1
Ld      F0, 0(R1)
Sd      F0, 0(R1)
Bne     R0, R1, 1
Beq     R0, R1, 1
```

You can also add comments using #.
```
# Don't forget to add a space after #
# Do not alloe extra blank lines in the program file like the following:

# That is not allowed
```
