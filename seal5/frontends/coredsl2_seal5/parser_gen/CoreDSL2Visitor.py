# Generated from CoreDSL2.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CoreDSL2Parser import CoreDSL2Parser
else:
    from CoreDSL2Parser import CoreDSL2Parser

# This class defines a complete generic visitor for a parse tree produced by CoreDSL2Parser.

class CoreDSL2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by CoreDSL2Parser#description_content.
    def visitDescription_content(self, ctx:CoreDSL2Parser.Description_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#import_file.
    def visitImport_file(self, ctx:CoreDSL2Parser.Import_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#instruction_set.
    def visitInstruction_set(self, ctx:CoreDSL2Parser.Instruction_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#core_def.
    def visitCore_def(self, ctx:CoreDSL2Parser.Core_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#section_arch_state.
    def visitSection_arch_state(self, ctx:CoreDSL2Parser.Section_arch_stateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#section_functions.
    def visitSection_functions(self, ctx:CoreDSL2Parser.Section_functionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#section_instructions.
    def visitSection_instructions(self, ctx:CoreDSL2Parser.Section_instructionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#section_always.
    def visitSection_always(self, ctx:CoreDSL2Parser.Section_alwaysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#always_block.
    def visitAlways_block(self, ctx:CoreDSL2Parser.Always_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#instruction.
    def visitInstruction(self, ctx:CoreDSL2Parser.InstructionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#rule_encoding.
    def visitRule_encoding(self, ctx:CoreDSL2Parser.Rule_encodingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#bit_value.
    def visitBit_value(self, ctx:CoreDSL2Parser.Bit_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#bit_field.
    def visitBit_field(self, ctx:CoreDSL2Parser.Bit_fieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#function_definition.
    def visitFunction_definition(self, ctx:CoreDSL2Parser.Function_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#parameter_list.
    def visitParameter_list(self, ctx:CoreDSL2Parser.Parameter_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#parameter_declaration.
    def visitParameter_declaration(self, ctx:CoreDSL2Parser.Parameter_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#block_statement.
    def visitBlock_statement(self, ctx:CoreDSL2Parser.Block_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#procedure_call.
    def visitProcedure_call(self, ctx:CoreDSL2Parser.Procedure_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#if_statement.
    def visitIf_statement(self, ctx:CoreDSL2Parser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#for_statement.
    def visitFor_statement(self, ctx:CoreDSL2Parser.For_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#while_statement.
    def visitWhile_statement(self, ctx:CoreDSL2Parser.While_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#do_statement.
    def visitDo_statement(self, ctx:CoreDSL2Parser.Do_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#switch_statement.
    def visitSwitch_statement(self, ctx:CoreDSL2Parser.Switch_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#return_statement.
    def visitReturn_statement(self, ctx:CoreDSL2Parser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#break_statement.
    def visitBreak_statement(self, ctx:CoreDSL2Parser.Break_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#continue_statement.
    def visitContinue_statement(self, ctx:CoreDSL2Parser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#spawn_statement.
    def visitSpawn_statement(self, ctx:CoreDSL2Parser.Spawn_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#expression_statement.
    def visitExpression_statement(self, ctx:CoreDSL2Parser.Expression_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#switch_block_statement_group.
    def visitSwitch_block_statement_group(self, ctx:CoreDSL2Parser.Switch_block_statement_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#switch_label.
    def visitSwitch_label(self, ctx:CoreDSL2Parser.Switch_labelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#block.
    def visitBlock(self, ctx:CoreDSL2Parser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#block_item.
    def visitBlock_item(self, ctx:CoreDSL2Parser.Block_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#for_condition.
    def visitFor_condition(self, ctx:CoreDSL2Parser.For_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#declaration.
    def visitDeclaration(self, ctx:CoreDSL2Parser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#type_specifier.
    def visitType_specifier(self, ctx:CoreDSL2Parser.Type_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#integer_type.
    def visitInteger_type(self, ctx:CoreDSL2Parser.Integer_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#float_type.
    def visitFloat_type(self, ctx:CoreDSL2Parser.Float_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#bool_type.
    def visitBool_type(self, ctx:CoreDSL2Parser.Bool_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#void_type.
    def visitVoid_type(self, ctx:CoreDSL2Parser.Void_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#composite_declaration.
    def visitComposite_declaration(self, ctx:CoreDSL2Parser.Composite_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#composite_reference.
    def visitComposite_reference(self, ctx:CoreDSL2Parser.Composite_referenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#enum_declaration.
    def visitEnum_declaration(self, ctx:CoreDSL2Parser.Enum_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#enum_reference.
    def visitEnum_reference(self, ctx:CoreDSL2Parser.Enum_referenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#integer_signedness.
    def visitInteger_signedness(self, ctx:CoreDSL2Parser.Integer_signednessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#integer_shorthand.
    def visitInteger_shorthand(self, ctx:CoreDSL2Parser.Integer_shorthandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#float_shorthand.
    def visitFloat_shorthand(self, ctx:CoreDSL2Parser.Float_shorthandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#attribute.
    def visitAttribute(self, ctx:CoreDSL2Parser.AttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#bit_size_specifier.
    def visitBit_size_specifier(self, ctx:CoreDSL2Parser.Bit_size_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#enumerator_list.
    def visitEnumerator_list(self, ctx:CoreDSL2Parser.Enumerator_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#enumerator.
    def visitEnumerator(self, ctx:CoreDSL2Parser.EnumeratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#struct_declaration.
    def visitStruct_declaration(self, ctx:CoreDSL2Parser.Struct_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#struct_declaration_specifier.
    def visitStruct_declaration_specifier(self, ctx:CoreDSL2Parser.Struct_declaration_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#declarator.
    def visitDeclarator(self, ctx:CoreDSL2Parser.DeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#initializer.
    def visitInitializer(self, ctx:CoreDSL2Parser.InitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#initializerList.
    def visitInitializerList(self, ctx:CoreDSL2Parser.InitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#designated_initializer.
    def visitDesignated_initializer(self, ctx:CoreDSL2Parser.Designated_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#designator.
    def visitDesignator(self, ctx:CoreDSL2Parser.DesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#cast_expression.
    def visitCast_expression(self, ctx:CoreDSL2Parser.Cast_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#binary_expression.
    def visitBinary_expression(self, ctx:CoreDSL2Parser.Binary_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#preinc_expression.
    def visitPreinc_expression(self, ctx:CoreDSL2Parser.Preinc_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#conditional_expression.
    def visitConditional_expression(self, ctx:CoreDSL2Parser.Conditional_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#deref_expression.
    def visitDeref_expression(self, ctx:CoreDSL2Parser.Deref_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#prefix_expression.
    def visitPrefix_expression(self, ctx:CoreDSL2Parser.Prefix_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#postinc_expression.
    def visitPostinc_expression(self, ctx:CoreDSL2Parser.Postinc_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#concat_expression.
    def visitConcat_expression(self, ctx:CoreDSL2Parser.Concat_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#assignment_expression.
    def visitAssignment_expression(self, ctx:CoreDSL2Parser.Assignment_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#method_call.
    def visitMethod_call(self, ctx:CoreDSL2Parser.Method_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#primary_expression.
    def visitPrimary_expression(self, ctx:CoreDSL2Parser.Primary_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#slice_expression.
    def visitSlice_expression(self, ctx:CoreDSL2Parser.Slice_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#reference_expression.
    def visitReference_expression(self, ctx:CoreDSL2Parser.Reference_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#constant_expression.
    def visitConstant_expression(self, ctx:CoreDSL2Parser.Constant_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#literal_expression.
    def visitLiteral_expression(self, ctx:CoreDSL2Parser.Literal_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#parens_expression.
    def visitParens_expression(self, ctx:CoreDSL2Parser.Parens_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#string_literal.
    def visitString_literal(self, ctx:CoreDSL2Parser.String_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#constant.
    def visitConstant(self, ctx:CoreDSL2Parser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#integer_constant.
    def visitInteger_constant(self, ctx:CoreDSL2Parser.Integer_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#floating_constant.
    def visitFloating_constant(self, ctx:CoreDSL2Parser.Floating_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#bool_constant.
    def visitBool_constant(self, ctx:CoreDSL2Parser.Bool_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#character_constant.
    def visitCharacter_constant(self, ctx:CoreDSL2Parser.Character_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#string_constant.
    def visitString_constant(self, ctx:CoreDSL2Parser.String_constantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#double_left_bracket.
    def visitDouble_left_bracket(self, ctx:CoreDSL2Parser.Double_left_bracketContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#double_right_bracket.
    def visitDouble_right_bracket(self, ctx:CoreDSL2Parser.Double_right_bracketContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#data_types.
    def visitData_types(self, ctx:CoreDSL2Parser.Data_typesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#type_qualifier.
    def visitType_qualifier(self, ctx:CoreDSL2Parser.Type_qualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#storage_class_specifier.
    def visitStorage_class_specifier(self, ctx:CoreDSL2Parser.Storage_class_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CoreDSL2Parser#struct_or_union.
    def visitStruct_or_union(self, ctx:CoreDSL2Parser.Struct_or_unionContext):
        return self.visitChildren(ctx)



del CoreDSL2Parser