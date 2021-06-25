%Result = type opaque
%Qubit = type opaque
%String = type opaque

declare %Result* @__quantum__rt__result_get_zero() local_unnamed_addr

declare i1 @__quantum__rt__result_equal(%Result*, %Result*) local_unnamed_addr

define internal fastcc double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body(i64 %nrIter) unnamed_addr {
entry:
  %target = tail call %Qubit* @__quantum__rt__qubit_allocate()
  %aux = tail call %Qubit* @__quantum__rt__qubit_allocate()
  tail call void @__quantum__qis__h__body(%Qubit* %target)
  %.not1 = icmp slt i64 %nrIter, 1
  br i1 %.not1, label %exit__1, label %body__1

body__1:                                          ; preds = %entry, %body__1
  %0 = phi i64 [ %13, %body__1 ], [ 1, %entry ]
  %sigma.03 = phi double [ %12, %body__1 ], [ 6.065000e-01, %entry ]
  %mu.02 = phi double [ %11, %body__1 ], [ 7.951000e-01, %entry ]
  %1 = fdiv double %mu.02, %sigma.03
  %2 = fsub double 0x3FF921FB54442D18, %1
  %3 = fmul double %sigma.03, 0x400921FB54442D18
  %4 = fmul double %3, 5.000000e-01
  %5 = fsub double %mu.02, %4
  %6 = fmul double %5, 0x400921FB54442D18
  tail call void @__quantum__qis__h__body(%Qubit* %aux)
  tail call void @__quantum__qis__rz__body(double %2, %Qubit* %aux)
  tail call void @__quantum__qis__crz__body(double %6, %Qubit* %aux, %Qubit* %target)
  tail call void @__quantum__qis__h__body(%Qubit* %aux)
  %result.i.i = tail call %Result* @__quantum__qis__m__body(%Qubit* %aux)
  tail call void @__quantum__qis__reset__body(%Qubit* %aux)
  %7 = tail call %Result* @__quantum__rt__result_get_zero()
  %8 = tail call i1 @__quantum__rt__result_equal(%Result* %result.i.i, %Result* %7)
  %9 = fmul double %sigma.03, 6.065000e-01
  %10 = fneg double %9
  %.p.i = select i1 %8, double %10, double %9
  %11 = fadd double %mu.02, %.p.i
  %12 = fmul double %sigma.03, 7.951000e-01
  tail call void @__quantum__rt__result_update_reference_count(%Result* %result.i.i, i32 -1)
  %13 = add i64 %0, 1
  %.not = icmp sgt i64 %13, %nrIter
  br i1 %.not, label %exit__1, label %body__1

exit__1:                                          ; preds = %body__1, %entry
  %mu.0.lcssa = phi double [ 7.951000e-01, %entry ], [ %11, %body__1 ]
  tail call void @__quantum__rt__qubit_release(%Qubit* %aux)
  tail call void @__quantum__rt__qubit_release(%Qubit* %target)
  ret double %mu.0.lcssa
}

declare %Qubit* @__quantum__rt__qubit_allocate() local_unnamed_addr

declare void @__quantum__rt__qubit_release(%Qubit*) local_unnamed_addr

declare void @__quantum__rt__result_update_reference_count(%Result*, i32) local_unnamed_addr

declare void @__quantum__qis__h__body(%Qubit*) local_unnamed_addr

declare void @__quantum__qis__rz__body(double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__crz__body(double, %Qubit*, %Qubit*) local_unnamed_addr

declare %Result* @__quantum__qis__m__body(%Qubit*) local_unnamed_addr

declare void @__quantum__qis__reset__body(%Qubit*) local_unnamed_addr

define double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__Interop(i64 %nrIter) local_unnamed_addr #0 {
entry:
  %0 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body(i64 %nrIter)
  ret double %0
}

define void @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk(i64 %nrIter) local_unnamed_addr #1 {
entry:
  %0 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body(i64 %nrIter)
  %1 = tail call %String* @__quantum__rt__double_to_string(double %0)
  tail call void @__quantum__rt__message(%String* %1)
  tail call void @__quantum__rt__string_update_reference_count(%String* %1, i32 -1)
  ret void
}

declare void @__quantum__rt__message(%String*) local_unnamed_addr

declare %String* @__quantum__rt__double_to_string(double) local_unnamed_addr

declare void @__quantum__rt__string_update_reference_count(%String*, i32) local_unnamed_addr

attributes #0 = { "InteropFriendly" }
attributes #1 = { "EntryPoint" }
