# Generated from CoreDSL2.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CoreDSL2Parser import CoreDSL2Parser
else:
    from CoreDSL2Parser import CoreDSL2Parser

# This class defines a complete listener for a parse tree produced by CoreDSL2Parser.
class CoreDSL2Listener(ParseTreeListener):

    # Enter a parse tree produced by CoreDSL2Parser#description_content.
    def enterDescription_content(self, ctx:CoreDSL2Parser.Description_contentContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#description_content.
    def exitDescription_content(self, ctx:CoreDSL2Parser.Description_contentContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#import_file.
    def enterImport_file(self, ctx:CoreDSL2Parser.Import_fileContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#import_file.
    def exitImport_file(self, ctx:CoreDSL2Parser.Import_fileContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#instruction_set.
    def enterInstruction_set(self, ctx:CoreDSL2Parser.Instruction_setContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#instruction_set.
    def exitInstruction_set(self, ctx:CoreDSL2Parser.Instruction_setContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#core_def.
    def enterCore_def(self, ctx:CoreDSL2Parser.Core_defContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#core_def.
    def exitCore_def(self, ctx:CoreDSL2Parser.Core_defContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#section_arch_state.
    def enterSection_arch_state(self, ctx:CoreDSL2Parser.Section_arch_stateContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#section_arch_state.
    def exitSection_arch_state(self, ctx:CoreDSL2Parser.Section_arch_stateContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#section_functions.
    def enterSection_functions(self, ctx:CoreDSL2Parser.Section_functionsContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#section_functions.
    def exitSection_functions(self, ctx:CoreDSL2Parser.Section_functionsContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#section_instructions.
    def enterSection_instructions(self, ctx:CoreDSL2Parser.Section_instructionsContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#section_instructions.
    def exitSection_instructions(self, ctx:CoreDSL2Parser.Section_instructionsContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#section_always.
    def enterSection_always(self, ctx:CoreDSL2Parser.Section_alwaysContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#section_always.
    def exitSection_always(self, ctx:CoreDSL2Parser.Section_alwaysContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#always_block.
    def enterAlways_block(self, ctx:CoreDSL2Parser.Always_blockContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#always_block.
    def exitAlways_block(self, ctx:CoreDSL2Parser.Always_blockContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#instruction.
    def enterInstruction(self, ctx:CoreDSL2Parser.InstructionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#instruction.
    def exitInstruction(self, ctx:CoreDSL2Parser.InstructionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#rule_encoding.
    def enterRule_encoding(self, ctx:CoreDSL2Parser.Rule_encodingContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#rule_encoding.
    def exitRule_encoding(self, ctx:CoreDSL2Parser.Rule_encodingContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#bit_value.
    def enterBit_value(self, ctx:CoreDSL2Parser.Bit_valueContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#bit_value.
    def exitBit_value(self, ctx:CoreDSL2Parser.Bit_valueContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#bit_field.
    def enterBit_field(self, ctx:CoreDSL2Parser.Bit_fieldContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#bit_field.
    def exitBit_field(self, ctx:CoreDSL2Parser.Bit_fieldContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#function_definition.
    def enterFunction_definition(self, ctx:CoreDSL2Parser.Function_definitionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#function_definition.
    def exitFunction_definition(self, ctx:CoreDSL2Parser.Function_definitionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#parameter_list.
    def enterParameter_list(self, ctx:CoreDSL2Parser.Parameter_listContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#parameter_list.
    def exitParameter_list(self, ctx:CoreDSL2Parser.Parameter_listContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#parameter_declaration.
    def enterParameter_declaration(self, ctx:CoreDSL2Parser.Parameter_declarationContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#parameter_declaration.
    def exitParameter_declaration(self, ctx:CoreDSL2Parser.Parameter_declarationContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#block_statement.
    def enterBlock_statement(self, ctx:CoreDSL2Parser.Block_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#block_statement.
    def exitBlock_statement(self, ctx:CoreDSL2Parser.Block_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#procedure_call.
    def enterProcedure_call(self, ctx:CoreDSL2Parser.Procedure_callContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#procedure_call.
    def exitProcedure_call(self, ctx:CoreDSL2Parser.Procedure_callContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#if_statement.
    def enterIf_statement(self, ctx:CoreDSL2Parser.If_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#if_statement.
    def exitIf_statement(self, ctx:CoreDSL2Parser.If_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#for_statement.
    def enterFor_statement(self, ctx:CoreDSL2Parser.For_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#for_statement.
    def exitFor_statement(self, ctx:CoreDSL2Parser.For_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#while_statement.
    def enterWhile_statement(self, ctx:CoreDSL2Parser.While_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#while_statement.
    def exitWhile_statement(self, ctx:CoreDSL2Parser.While_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#do_statement.
    def enterDo_statement(self, ctx:CoreDSL2Parser.Do_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#do_statement.
    def exitDo_statement(self, ctx:CoreDSL2Parser.Do_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#switch_statement.
    def enterSwitch_statement(self, ctx:CoreDSL2Parser.Switch_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#switch_statement.
    def exitSwitch_statement(self, ctx:CoreDSL2Parser.Switch_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#return_statement.
    def enterReturn_statement(self, ctx:CoreDSL2Parser.Return_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#return_statement.
    def exitReturn_statement(self, ctx:CoreDSL2Parser.Return_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#break_statement.
    def enterBreak_statement(self, ctx:CoreDSL2Parser.Break_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#break_statement.
    def exitBreak_statement(self, ctx:CoreDSL2Parser.Break_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#continue_statement.
    def enterContinue_statement(self, ctx:CoreDSL2Parser.Continue_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#continue_statement.
    def exitContinue_statement(self, ctx:CoreDSL2Parser.Continue_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#spawn_statement.
    def enterSpawn_statement(self, ctx:CoreDSL2Parser.Spawn_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#spawn_statement.
    def exitSpawn_statement(self, ctx:CoreDSL2Parser.Spawn_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#expression_statement.
    def enterExpression_statement(self, ctx:CoreDSL2Parser.Expression_statementContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#expression_statement.
    def exitExpression_statement(self, ctx:CoreDSL2Parser.Expression_statementContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#switch_block_statement_group.
    def enterSwitch_block_statement_group(self, ctx:CoreDSL2Parser.Switch_block_statement_groupContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#switch_block_statement_group.
    def exitSwitch_block_statement_group(self, ctx:CoreDSL2Parser.Switch_block_statement_groupContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#switch_label.
    def enterSwitch_label(self, ctx:CoreDSL2Parser.Switch_labelContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#switch_label.
    def exitSwitch_label(self, ctx:CoreDSL2Parser.Switch_labelContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#block.
    def enterBlock(self, ctx:CoreDSL2Parser.BlockContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#block.
    def exitBlock(self, ctx:CoreDSL2Parser.BlockContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#block_item.
    def enterBlock_item(self, ctx:CoreDSL2Parser.Block_itemContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#block_item.
    def exitBlock_item(self, ctx:CoreDSL2Parser.Block_itemContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#for_condition.
    def enterFor_condition(self, ctx:CoreDSL2Parser.For_conditionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#for_condition.
    def exitFor_condition(self, ctx:CoreDSL2Parser.For_conditionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#declaration.
    def enterDeclaration(self, ctx:CoreDSL2Parser.DeclarationContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#declaration.
    def exitDeclaration(self, ctx:CoreDSL2Parser.DeclarationContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#type_specifier.
    def enterType_specifier(self, ctx:CoreDSL2Parser.Type_specifierContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#type_specifier.
    def exitType_specifier(self, ctx:CoreDSL2Parser.Type_specifierContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#integer_type.
    def enterInteger_type(self, ctx:CoreDSL2Parser.Integer_typeContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#integer_type.
    def exitInteger_type(self, ctx:CoreDSL2Parser.Integer_typeContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#float_type.
    def enterFloat_type(self, ctx:CoreDSL2Parser.Float_typeContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#float_type.
    def exitFloat_type(self, ctx:CoreDSL2Parser.Float_typeContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#bool_type.
    def enterBool_type(self, ctx:CoreDSL2Parser.Bool_typeContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#bool_type.
    def exitBool_type(self, ctx:CoreDSL2Parser.Bool_typeContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#void_type.
    def enterVoid_type(self, ctx:CoreDSL2Parser.Void_typeContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#void_type.
    def exitVoid_type(self, ctx:CoreDSL2Parser.Void_typeContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#composite_declaration.
    def enterComposite_declaration(self, ctx:CoreDSL2Parser.Composite_declarationContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#composite_declaration.
    def exitComposite_declaration(self, ctx:CoreDSL2Parser.Composite_declarationContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#composite_reference.
    def enterComposite_reference(self, ctx:CoreDSL2Parser.Composite_referenceContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#composite_reference.
    def exitComposite_reference(self, ctx:CoreDSL2Parser.Composite_referenceContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#enum_declaration.
    def enterEnum_declaration(self, ctx:CoreDSL2Parser.Enum_declarationContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#enum_declaration.
    def exitEnum_declaration(self, ctx:CoreDSL2Parser.Enum_declarationContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#enum_reference.
    def enterEnum_reference(self, ctx:CoreDSL2Parser.Enum_referenceContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#enum_reference.
    def exitEnum_reference(self, ctx:CoreDSL2Parser.Enum_referenceContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#integer_signedness.
    def enterInteger_signedness(self, ctx:CoreDSL2Parser.Integer_signednessContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#integer_signedness.
    def exitInteger_signedness(self, ctx:CoreDSL2Parser.Integer_signednessContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#integer_shorthand.
    def enterInteger_shorthand(self, ctx:CoreDSL2Parser.Integer_shorthandContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#integer_shorthand.
    def exitInteger_shorthand(self, ctx:CoreDSL2Parser.Integer_shorthandContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#float_shorthand.
    def enterFloat_shorthand(self, ctx:CoreDSL2Parser.Float_shorthandContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#float_shorthand.
    def exitFloat_shorthand(self, ctx:CoreDSL2Parser.Float_shorthandContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#attribute.
    def enterAttribute(self, ctx:CoreDSL2Parser.AttributeContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#attribute.
    def exitAttribute(self, ctx:CoreDSL2Parser.AttributeContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#bit_size_specifier.
    def enterBit_size_specifier(self, ctx:CoreDSL2Parser.Bit_size_specifierContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#bit_size_specifier.
    def exitBit_size_specifier(self, ctx:CoreDSL2Parser.Bit_size_specifierContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#enumerator_list.
    def enterEnumerator_list(self, ctx:CoreDSL2Parser.Enumerator_listContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#enumerator_list.
    def exitEnumerator_list(self, ctx:CoreDSL2Parser.Enumerator_listContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#enumerator.
    def enterEnumerator(self, ctx:CoreDSL2Parser.EnumeratorContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#enumerator.
    def exitEnumerator(self, ctx:CoreDSL2Parser.EnumeratorContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#struct_declaration.
    def enterStruct_declaration(self, ctx:CoreDSL2Parser.Struct_declarationContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#struct_declaration.
    def exitStruct_declaration(self, ctx:CoreDSL2Parser.Struct_declarationContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#struct_declaration_specifier.
    def enterStruct_declaration_specifier(self, ctx:CoreDSL2Parser.Struct_declaration_specifierContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#struct_declaration_specifier.
    def exitStruct_declaration_specifier(self, ctx:CoreDSL2Parser.Struct_declaration_specifierContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#declarator.
    def enterDeclarator(self, ctx:CoreDSL2Parser.DeclaratorContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#declarator.
    def exitDeclarator(self, ctx:CoreDSL2Parser.DeclaratorContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#initializer.
    def enterInitializer(self, ctx:CoreDSL2Parser.InitializerContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#initializer.
    def exitInitializer(self, ctx:CoreDSL2Parser.InitializerContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#initializerList.
    def enterInitializerList(self, ctx:CoreDSL2Parser.InitializerListContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#initializerList.
    def exitInitializerList(self, ctx:CoreDSL2Parser.InitializerListContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#designated_initializer.
    def enterDesignated_initializer(self, ctx:CoreDSL2Parser.Designated_initializerContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#designated_initializer.
    def exitDesignated_initializer(self, ctx:CoreDSL2Parser.Designated_initializerContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#designator.
    def enterDesignator(self, ctx:CoreDSL2Parser.DesignatorContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#designator.
    def exitDesignator(self, ctx:CoreDSL2Parser.DesignatorContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#cast_expression.
    def enterCast_expression(self, ctx:CoreDSL2Parser.Cast_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#cast_expression.
    def exitCast_expression(self, ctx:CoreDSL2Parser.Cast_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#binary_expression.
    def enterBinary_expression(self, ctx:CoreDSL2Parser.Binary_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#binary_expression.
    def exitBinary_expression(self, ctx:CoreDSL2Parser.Binary_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#preinc_expression.
    def enterPreinc_expression(self, ctx:CoreDSL2Parser.Preinc_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#preinc_expression.
    def exitPreinc_expression(self, ctx:CoreDSL2Parser.Preinc_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#conditional_expression.
    def enterConditional_expression(self, ctx:CoreDSL2Parser.Conditional_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#conditional_expression.
    def exitConditional_expression(self, ctx:CoreDSL2Parser.Conditional_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#deref_expression.
    def enterDeref_expression(self, ctx:CoreDSL2Parser.Deref_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#deref_expression.
    def exitDeref_expression(self, ctx:CoreDSL2Parser.Deref_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#prefix_expression.
    def enterPrefix_expression(self, ctx:CoreDSL2Parser.Prefix_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#prefix_expression.
    def exitPrefix_expression(self, ctx:CoreDSL2Parser.Prefix_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#postinc_expression.
    def enterPostinc_expression(self, ctx:CoreDSL2Parser.Postinc_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#postinc_expression.
    def exitPostinc_expression(self, ctx:CoreDSL2Parser.Postinc_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#concat_expression.
    def enterConcat_expression(self, ctx:CoreDSL2Parser.Concat_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#concat_expression.
    def exitConcat_expression(self, ctx:CoreDSL2Parser.Concat_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#assignment_expression.
    def enterAssignment_expression(self, ctx:CoreDSL2Parser.Assignment_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#assignment_expression.
    def exitAssignment_expression(self, ctx:CoreDSL2Parser.Assignment_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#method_call.
    def enterMethod_call(self, ctx:CoreDSL2Parser.Method_callContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#method_call.
    def exitMethod_call(self, ctx:CoreDSL2Parser.Method_callContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#primary_expression.
    def enterPrimary_expression(self, ctx:CoreDSL2Parser.Primary_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#primary_expression.
    def exitPrimary_expression(self, ctx:CoreDSL2Parser.Primary_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#slice_expression.
    def enterSlice_expression(self, ctx:CoreDSL2Parser.Slice_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#slice_expression.
    def exitSlice_expression(self, ctx:CoreDSL2Parser.Slice_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#reference_expression.
    def enterReference_expression(self, ctx:CoreDSL2Parser.Reference_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#reference_expression.
    def exitReference_expression(self, ctx:CoreDSL2Parser.Reference_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#constant_expression.
    def enterConstant_expression(self, ctx:CoreDSL2Parser.Constant_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#constant_expression.
    def exitConstant_expression(self, ctx:CoreDSL2Parser.Constant_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#literal_expression.
    def enterLiteral_expression(self, ctx:CoreDSL2Parser.Literal_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#literal_expression.
    def exitLiteral_expression(self, ctx:CoreDSL2Parser.Literal_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#parens_expression.
    def enterParens_expression(self, ctx:CoreDSL2Parser.Parens_expressionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#parens_expression.
    def exitParens_expression(self, ctx:CoreDSL2Parser.Parens_expressionContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#string_literal.
    def enterString_literal(self, ctx:CoreDSL2Parser.String_literalContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#string_literal.
    def exitString_literal(self, ctx:CoreDSL2Parser.String_literalContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#constant.
    def enterConstant(self, ctx:CoreDSL2Parser.ConstantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#constant.
    def exitConstant(self, ctx:CoreDSL2Parser.ConstantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#integer_constant.
    def enterInteger_constant(self, ctx:CoreDSL2Parser.Integer_constantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#integer_constant.
    def exitInteger_constant(self, ctx:CoreDSL2Parser.Integer_constantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#floating_constant.
    def enterFloating_constant(self, ctx:CoreDSL2Parser.Floating_constantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#floating_constant.
    def exitFloating_constant(self, ctx:CoreDSL2Parser.Floating_constantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#bool_constant.
    def enterBool_constant(self, ctx:CoreDSL2Parser.Bool_constantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#bool_constant.
    def exitBool_constant(self, ctx:CoreDSL2Parser.Bool_constantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#character_constant.
    def enterCharacter_constant(self, ctx:CoreDSL2Parser.Character_constantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#character_constant.
    def exitCharacter_constant(self, ctx:CoreDSL2Parser.Character_constantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#string_constant.
    def enterString_constant(self, ctx:CoreDSL2Parser.String_constantContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#string_constant.
    def exitString_constant(self, ctx:CoreDSL2Parser.String_constantContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#double_left_bracket.
    def enterDouble_left_bracket(self, ctx:CoreDSL2Parser.Double_left_bracketContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#double_left_bracket.
    def exitDouble_left_bracket(self, ctx:CoreDSL2Parser.Double_left_bracketContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#double_right_bracket.
    def enterDouble_right_bracket(self, ctx:CoreDSL2Parser.Double_right_bracketContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#double_right_bracket.
    def exitDouble_right_bracket(self, ctx:CoreDSL2Parser.Double_right_bracketContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#data_types.
    def enterData_types(self, ctx:CoreDSL2Parser.Data_typesContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#data_types.
    def exitData_types(self, ctx:CoreDSL2Parser.Data_typesContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#type_qualifier.
    def enterType_qualifier(self, ctx:CoreDSL2Parser.Type_qualifierContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#type_qualifier.
    def exitType_qualifier(self, ctx:CoreDSL2Parser.Type_qualifierContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#storage_class_specifier.
    def enterStorage_class_specifier(self, ctx:CoreDSL2Parser.Storage_class_specifierContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#storage_class_specifier.
    def exitStorage_class_specifier(self, ctx:CoreDSL2Parser.Storage_class_specifierContext):
        pass


    # Enter a parse tree produced by CoreDSL2Parser#struct_or_union.
    def enterStruct_or_union(self, ctx:CoreDSL2Parser.Struct_or_unionContext):
        pass

    # Exit a parse tree produced by CoreDSL2Parser#struct_or_union.
    def exitStruct_or_union(self, ctx:CoreDSL2Parser.Struct_or_unionContext):
        pass



del CoreDSL2Parser