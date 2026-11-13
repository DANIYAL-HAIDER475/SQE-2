
The objective of this part is to perform white-box testing on the provided Student Course Registration System.

The testing focuses on the internal control flow of `registration_decision()`, cyclomatic complexity, statement and branch coverage, condition coverage, MC/DC analysis, and pytest test implementation.

Expected results are derived from the Software Requirements Specification (SRS). The original implementation is preserved during initial testing so that existing defects can be identified and documented.

## 2. B1 – Control Flow Graph (CFG) and Cyclomatic Complexity

The selected function for control-flow analysis is:

`registration_decision(student, course)`

The function checks:

- Invalid outstanding dues.
- Invalid course capacity and enrollment.
- Outstanding dues blocking.
- Already registered students.
- Missing prerequisites.
- Credit-hour eligibility.
- Course availability.

### Cyclomatic Complexity

The formula is:

`V(G) = E - N + 2`

The alternative formula is:

`V(G) = D + 1`

For this analysis, the compound capacity-validation expression is expanded into three atomic conditions:

- A: `0 <= course.enrolled`
- B: `course.enrolled <= course.capacity`
- C: `course.capacity < 1`

There are nine decision points under this expanded convention.

`V(G) = 9 + 1 = 10`

Therefore, the theoretical basis-path count for this expanded control-flow graph is 10.

The CFG is saved separately as:

`docs/whitebox_cfg.png`

**Note:** The exact edge count (E) and node count (N) must be counted from the final CFG diagram. They should satisfy `E - N + 2 = 10`.

### Independent Paths

| Path | Description | Test ID |
|---|---|---|
| P1 | Invalid outstanding dues | WB01 |
| P2 | Negative enrollment | WB08 |
| P3 | Enrollment exceeds capacity during validation | WB02 |
| P4 | Invalid course capacity | WB09 |
| P5 | Outstanding dues block registration | WB03 |
| P6 | Student already registered | WB04 |
| P7 | Prerequisites missing | WB05 |
| P8 | Credit limit exceeded | WB06 |
| P9 | Waitlist decision | WB15 |
| P10 | Successful registration decision | WB07 |

**Infeasible path:** P9 cannot be reached in the original implementation. The earlier capacity validation rejects enrollment greater than capacity, but the later waitlist condition checks for exactly that situation. WB15 is retained as a requirements-based test to expose this defect.

## 3. B2 – Statement and Branch Coverage

White-box coverage was measured using `pytest` and `pytest-cov`.

Command:

```bash
python -m pytest tests/test_whitebox.py --cov=registration --cov-branch --cov-report=term-missing
```

### Initial nine-test baseline

The initial white-box test run produced:

- Tests passed: 9
- Reported coverage: 68%
- Statements missed: 16

### Expanded 16-test run

After adding further white-box tests, the coverage report showed:

- Tests executed: 16
- Statements missed: 3
- Total branches: 26
- Partially covered branches: 2
- Reported overall coverage: 91%
- Missing lines: 59, 70–71

The remaining uncovered locations relate to paths that were not executed by the test suite.

The two waitlist tests were also checked against the SRS-required result. Both exposed the waitlist defect in the original implementation.

**Scope note:** The 68% result is the initial nine-test white-box baseline, not a black-box-only baseline. This individual report records the white-box measurements available from the individual test suite. It does not claim that black-box coverage was measured.

## 4. B3 – Condition Coverage and MC/DC

The compound capacity-validation expression is:

```python
if not 0 <= course.enrolled <= course.capacity or course.capacity < 1:
```

### Atomic conditions

- A: `0 <= course.enrolled`
- B: `course.enrolled <= course.capacity`
- C: `course.capacity < 1`

### Condition table

| Test | A | B | C | Decision |
|---|---|---|---|---|
| WB08 | False | Not evaluated | Not evaluated | True |
| WB02 | True | False | Not evaluated | True |
| WB07 | True | True | False | False |
| WB09 | True | True | True | True |

Python uses short-circuit evaluation. Therefore, some conditions are not evaluated when an earlier condition determines the result.

### MC/DC analysis

| Condition | Test pair | Demonstrated effect |
|---|---|---|
| A | WB08 and WB07 | A changes the decision result |
| B | WB02 and WB07 | B changes the decision result |
| C | WB07 and WB09 | C changes the decision result |

The A pair uses masking due to short-circuit evaluation: when A is false, the remaining conditions are not evaluated. The B and C pairs demonstrate their independent effects while the other relevant conditions remain unchanged.

Condition coverage and MC/DC are analyzed manually because `pytest-cov` reports statement and branch coverage, not MC/DC directly.

## 5. B4 – White-Box Pytest Tests

A separate white-box test file was implemented:

`tests/test_whitebox.py`

The test suite contains 16 test cases.

| Test ID | Purpose | Target |
|---|---|---|
| WB01 | Invalid outstanding dues | Exception path |
| WB02 | Invalid enrollment/capacity | Capacity-validation branch |
| WB03 | Outstanding dues blocking | Dues decision |
| WB04 | Already registered student | Duplicate-registration branch |
| WB05 | Missing prerequisites | Prerequisite branch |
| WB06 | Credit limit exceeded | Credit-limit branch |
| WB07 | Successful registration decision | Final registration path |
| WB08 | Negative enrollment | Condition A |
| WB09 | Zero capacity | Condition C |
| WB10 | Successful course registration | Registration state update |
| WB11 | Successful withdrawal | Withdrawal true branch |
| WB12 | Withdrawal of an unregistered course | Withdrawal false branch |
| WB13 | Invalid current credits | Credit validation exception |
| WB14 | Invalid course credits | Credit validation exception |
| WB15 | Full-course waitlist behavior | Waitlist requirement |
| WB16 | Existing waitlist behavior | Duplicate waitlist handling |

### Test execution and defect evidence

The initial implementation-matching version of the suite produced 16 passing tests.

The two waitlist tests were then checked using the SRS-required expected result, `WAITLISTED`. Both failed because the original implementation returned `REGISTERED`.

These failures are retained as evidence of a requirements-related defect. They must not be changed to successful expected results merely to make the test suite pass.

## 6. Defects Identified

The following defects were identified by comparing the implementation with the SRS:

1. **Credit limit:** The implementation uses `< 18`, rejecting exactly 18 credits, although the SRS permits a total of 18.
2. **Prerequisites:** The implementation checks whether any required prerequisite is completed instead of requiring all required prerequisites.
3. **Outstanding dues:** The implementation blocks only dues greater than 1000, while the SRS requires blocking any positive outstanding dues.
4. **Waitlist:** A course at full capacity is incorrectly treated as available for registration. The later `enrolled > capacity` check is unreachable after the earlier validation.
5. **Withdrawal:** The implementation does not decrease `course.enrolled` after a successful withdrawal.

The original implementation was preserved during initial testing. These defects should be corrected separately and tested through regression testing.

## 7. Conclusion

White-box testing was performed on the Student Course Registration System using control-flow analysis, cyclomatic complexity, statement and branch coverage, condition analysis, MC/DC, and pytest.

The expanded white-box suite contained 16 tests and produced a reported overall coverage of 91% in the recorded coverage run. The requirements-based waitlist tests exposed two failures in the original implementation.

The analysis also identified five defects related to credit limits, prerequisites, outstanding dues, waitlist handling, and course withdrawal.

The CFG, test cases, coverage evidence, and defect observations provide a basis for further correction and regression testing.

**Files produced for Part B:**

- `tests/test_whitebox.py`
- `docs/whitebox_cfg.png`
- `docs/whitebox_report.md`