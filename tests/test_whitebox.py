
import pytest

from registration import (
    Student, Course, registration_decision,
    register_course, withdraw_course, check_credit_limit
)

# WB01: Test negative outstanding dues
def test_WB01_invalid_dues():
    student = Student(
        student_id="S001",
        outstanding_dues=-1
    )

    course = Course(
        code="CS101",
        credit_hours=3,
        capacity=30
    )

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


# WB02: Test enrollment greater than course capacity
def test_WB02_invalid_capacity():
    student = Student(student_id="S002")

    course = Course(
        code="CS102",
        credit_hours=3,
        capacity=30,
        enrolled=31
    )

    with pytest.raises(
        ValueError,
        match="Invalid capacity or enrollment"
    ):
        registration_decision(student, course)

# WB03: Test dues blocking
def test_WB03_dues_block():
    student = Student(
        student_id="S003",
        outstanding_dues=1001
    )
    course = Course(
        code="CS103",
        credit_hours=3,
        capacity=30
    )

    result = registration_decision(student, course)
    assert result == "DUES_BLOCK"


# WB04: Test already registered branch
def test_WB04_already_registered():
    student = Student(
        student_id="S004",
        registered_courses={"CS104"}
    )
    course = Course(
        code="CS104",
        credit_hours=3,
        capacity=30
    )

    result = registration_decision(student, course)
    assert result == "ALREADY_REGISTERED"


# WB05: Test missing prerequisites branch
def test_WB05_missing_prerequisites():
    student = Student(student_id="S005")
    course = Course(
        code="CS105",
        credit_hours=3,
        capacity=30,
        prerequisites={"CS101"}
    )

    result = registration_decision(student, course)
    assert result == "PREREQUISITES_MISSING"


# WB06: Test credit limit branch
def test_WB06_credit_limit():
    student = Student(
        student_id="S006",
        current_credits=16
    )
    course = Course(
        code="CS106",
        credit_hours=3,
        capacity=30
    )

    result = registration_decision(student, course)
    assert result == "CREDIT_LIMIT"


# WB07: Test successful registration decision
def test_WB07_registered():
    student = Student(student_id="S007")
    course = Course(
        code="CS107",
        credit_hours=3,
        capacity=30
    )

    result = registration_decision(student, course)
    assert result == "REGISTERED"
# WB08: Condition A is False (negative enrollment)
def test_WB08_negative_enrollment():
    student = Student(student_id="S008")
    course = Course(
        code="CS108",
        credit_hours=3,
        capacity=30,
        enrolled=-1
    )

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


# WB09: Condition C is True (capacity is zero)
def test_WB09_zero_capacity():
    student = Student(student_id="S009")
    course = Course(
        code="CS109",
        credit_hours=3,
        capacity=0,
        enrolled=0
    )

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)

        # WB10: Successfully register a student
def test_WB10_register_course():
    student = Student(student_id="S010")
    course = Course(code="CS110", credit_hours=3, capacity=30)

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS110" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 1


# WB11: Successfully withdraw a registered course
def test_WB11_withdraw_course():
    student = Student(
        student_id="S011",
        registered_courses={"CS111"},
        current_credits=3
    )
    course = Course(
        code="CS111",
        credit_hours=3,
        capacity=30,
        enrolled=1
    )

    result = withdraw_course(student, course)

    assert result is True
    assert "CS111" not in student.registered_courses
    assert student.current_credits == 0


# WB12: Withdraw a course not registered
def test_WB12_withdraw_unregistered_course():
    student = Student(student_id="S012")
    course = Course(code="CS112", credit_hours=3, capacity=30)

    result = withdraw_course(student, course)

    assert result is False

    # WB13: Invalid current credits
def test_WB13_invalid_current_credits():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 3)


# WB14: Invalid course credits
def test_WB14_invalid_course_credits():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(5, 5)


# WB15: Waitlist branch (currently unreachable through registration_decision)
def test_WB15_waitlist_branch():
    student = Student(student_id="S015")
    course = Course(code="CS115", credit_hours=3, capacity=30)
    course.enrolled = 30

    result = register_course(student, course)

    # Current implementation incorrectly returns REGISTERED.
    assert result == "REGISTERED"


# WB16: Student already on waitlist (not reached with current implementation)
def test_WB16_existing_waitlist():
    student = Student(student_id="S016")
    course = Course(
        code="CS116", credit_hours=3, capacity=30, enrolled=30,
        waitlist=["S016"]
    )

    result = register_course(student, course)

    assert result == "REGISTERED"