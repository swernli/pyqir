%Result = type opaque
%Qubit = type opaque
%String = type opaque

; Function Attrs: noinline norecurse nounwind readnone
define internal fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalComputeInput1__body(double %mu, double %sigma) unnamed_addr #0 {
entry:
  %0 = fdiv double %mu, %sigma
  %1 = fsub double 0x3FF921FB54442D18, %0
  ret double %1
}

; Function Attrs: noinline norecurse nounwind readnone
define internal fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalComputeInput2__body(double %mu, double %sigma) unnamed_addr #0 {
entry:
  %0 = fmul double %sigma, 0x400921FB54442D18
  %1 = fmul double %0, 5.000000e-01
  %2 = fsub double %mu, %1
  %3 = fmul double %2, 0x400921FB54442D18
  ret double %3
}

; Function Attrs: noinline
define internal fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalUpdateMu__body(double %mu, double %sigma, %Result* %res) unnamed_addr #1 {
entry:
  %0 = tail call %Result* @__quantum__rt__result_get_zero()
  %1 = tail call i1 @__quantum__rt__result_equal(%Result* %res, %Result* %0)
  %2 = fmul double %sigma, 6.065000e-01
  %3 = fneg double %2
  %.p = select i1 %1, double %3, double %2
  %4 = fadd double %.p, %mu
  ret double %4
}

declare %Result* @__quantum__rt__result_get_zero() local_unnamed_addr

declare i1 @__quantum__rt__result_equal(%Result*, %Result*) local_unnamed_addr

; Function Attrs: noinline norecurse nounwind readnone
define internal fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalUpdateSigma__body(double %sigma) unnamed_addr #0 {
entry:
  %0 = fmul double %sigma, 7.951000e-01
  ret double %0
}

define internal fastcc double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body(i64 %nrIter) unnamed_addr {
entry:
  %target = tail call %Qubit* @__quantum__rt__qubit_allocate()
  %aux = tail call %Qubit* @__quantum__rt__qubit_allocate()
  tail call fastcc void @Microsoft__Quantum__Qir__Emission__Prepare__body(%Qubit* %target)
  %.not1 = icmp slt i64 %nrIter, 1
  br i1 %.not1, label %exit__1, label %body__1

body__1:                                          ; preds = %entry, %body__1
  %0 = phi i64 [ %3, %body__1 ], [ 1, %entry ]
  %sigma.03 = phi double [ %2, %body__1 ], [ 6.065000e-01, %entry ]
  %mu.02 = phi double [ %1, %body__1 ], [ 7.951000e-01, %entry ]
  %c1 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalComputeInput1__body(double %mu.02, double %sigma.03)
  %c2 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalComputeInput2__body(double %mu.02, double %sigma.03)
  %datum = tail call fastcc %Result* @Microsoft__Quantum__Qir__Emission__Iterate__body(double %c1, double %c2, %Qubit* %target, %Qubit* %aux)
  %1 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalUpdateMu__body(double %mu.02, double %sigma.03, %Result* %datum)
  %2 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__ClassicalUpdateSigma__body(double %sigma.03)
  tail call void @__quantum__rt__result_update_reference_count(%Result* %datum, i32 -1)
  %3 = add i64 %0, 1
  %.not = icmp sgt i64 %3, %nrIter
  br i1 %.not, label %exit__1, label %body__1

exit__1:                                          ; preds = %body__1, %entry
  %mu.0.lcssa = phi double [ 7.951000e-01, %entry ], [ %1, %body__1 ]
  tail call void @__quantum__rt__qubit_release(%Qubit* %aux)
  tail call void @__quantum__rt__qubit_release(%Qubit* %target)
  ret double %mu.0.lcssa
}

declare %Qubit* @__quantum__rt__qubit_allocate() local_unnamed_addr

declare void @__quantum__rt__qubit_release(%Qubit*) local_unnamed_addr

; Function Attrs: noinline
define internal fastcc void @Microsoft__Quantum__Qir__Emission__Prepare__body(%Qubit* %target) unnamed_addr #2 {
entry:
  tail call void @__quantum__qis__h__body(%Qubit* %target)
  ret void
}

; Function Attrs: noinline
define internal fastcc %Result* @Microsoft__Quantum__Qir__Emission__Iterate__body(double %c1, double %c2, %Qubit* %target, %Qubit* %aux) unnamed_addr #2 {
entry:
  tail call void @__quantum__qis__h__body(%Qubit* %aux)
  tail call void @__quantum__qis__rz__body(double %c1, %Qubit* %aux)
  tail call void @__quantum__qis__crz__body(double %c2, %Qubit* %aux, %Qubit* %target)
  tail call void @__quantum__qis__h__body(%Qubit* %aux)
  %result.i = tail call %Result* @__quantum__qis__m__body(%Qubit* %aux)
  tail call void @__quantum__qis__reset__body(%Qubit* %aux)
  ret %Result* %result.i
}

declare void @__quantum__rt__result_update_reference_count(%Result*, i32) local_unnamed_addr

declare void @__quantum__qis__h__body(%Qubit*) local_unnamed_addr

declare void @__quantum__qis__rz__body(double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__crz__body(double, %Qubit*, %Qubit*) local_unnamed_addr

declare %Result* @__quantum__qis__m__body(%Qubit*) local_unnamed_addr

declare void @__quantum__qis__reset__body(%Qubit*) local_unnamed_addr

define double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__Interop(i64 %nrIter) local_unnamed_addr #3 {
entry:
  %0 = tail call fastcc double @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk__body(i64 %nrIter)
  ret double %0
}

define void @Microsoft__Quantum__Qir__Emission__EstimatePhaseByRandomWalk(i64 %nrIter) local_unnamed_addr #4 {
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

attributes #0 = { noinline norecurse nounwind readnone "ClassicalProcedure" }
attributes #1 = { noinline "ClassicalProcedure" }
attributes #2 = { noinline "QuantumProcedure" }
attributes #3 = { "InteropFriendly" }
attributes #4 = { "EntryPoint" }
