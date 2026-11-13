import pytest
from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course
)


# ==============================
# ECP AND BVA - CREDIT LIMIT
# ==============================

@pytest.mark.parametrize("current,new,expected", [
    (0, 1, True),
    (10, 4, True),
    (15, 3, True),
    (16, 3, False),
    (18, 1, False),
    (14, 4, True),
])
def test_credit_limit(current, new, expected):
    assert check_credit_limit(current, new) == expected


@pytest.mark.parametrize("current,new,error", [
    (-1, 2, "Invalid current credits"),
    (19, 2, "Invalid current credits"),
    (5, 0, "Invalid course credits"),
    (5, 5, "Invalid course credits"),
])
def test_invalid_credits(current, new, error):
    with pytest.raises(ValueError, match=error):
        check_credit_limit(current, new)


# ==============================
# ECP - PREREQUISITES
# ==============================

def test_no_prerequisites():
    assert prerequisites_satisfied(set(), set()) is True


def test_all_prerequisites_completed():
    assert prerequisites_satisfied(
        {"CS101", "MATH101"},
        {"CS101", "MATH101"}
    ) is True


def test_some_prerequisites_missing():
    assert prerequisites_satisfied(
        {"CS101"},
        {"CS101", "MATH101"}
    ) is False


def test_no_prerequisites_completed():
    assert prerequisites_satisfied(
        set(),
        {"CS101"}
    ) is False


# ==============================
# ECP AND BVA - REGISTRATION
# ==============================

def test_zero_dues_registration():
    student = Student("S1")
    course = Course("CS201", 3, 30)

    assert registration_decision(student, course) == "REGISTERED"


def test_positive_dues_block():
    student = Student("S1", outstanding_dues=1)
    course = Course("CS201", 3, 30)

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_already_registered():
    student = Student("S1", registered_courses={"CS201"})
    course = Course("CS201", 3, 30)

    assert registration_decision(student, course) == "ALREADY_REGISTERED"


def test_missing_prerequisites():
    student = Student("S1")
    course = Course("CS201", 3, 30, prerequisites={"CS101"})

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


def test_credit_limit_reached():
    student = Student("S1", current_credits=16)
    course = Course("CS201", 3, 30)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


def test_course_full():
    student = Student("S1")
    course = Course("CS201", 3, 30, enrolled=30)

    assert registration_decision(student, course) == "WAITLISTED"


def test_course_has_available_seat():
    student = Student("S1")
    course = Course("CS201", 3, 30, enrolled=29)

    assert registration_decision(student, course) == "REGISTERED"


# ==============================
# DECISION TABLE - PRIORITY
# ==============================

def test_dues_have_highest_priority():
    student = Student(
        "S1",
        outstanding_dues=100,
        registered_courses={"CS201"}
    )
    course = Course("CS201", 3, 30)

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_already_registered_priority():
    student = Student(
        "S1",
        registered_courses={"CS201"}
    )
    course = Course(
        "CS201", 3, 30,
        prerequisites={"CS101"}
    )

    assert registration_decision(student, course) == "ALREADY_REGISTERED"


def test_prerequisites_priority():
    student = Student("S1", current_credits=16)
    course = Course(
        "CS201", 3, 30,
        prerequisites={"CS101"}
    )

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


# ==============================
# STATE TRANSITION TESTING
# ==============================

def test_successful_registration_updates_state():
    student = Student("S1")
    course = Course("CS201", 3, 30)

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS201" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 1


def test_waitlist_registration():
    student = Student("S1")
    course = Course("CS201", 3, 30, enrolled=30)

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert "S1" in course.waitlist
    assert student.current_credits == 0
    assert course.enrolled == 30


def test_duplicate_waitlist_entry():
    student = Student("S1")
    course = Course("CS201", 3, 30, enrolled=30)
    course.waitlist.append("S1")

    register_course(student, course)

    assert course.waitlist.count("S1") == 1


def test_failed_registration_no_state_change():
    student = Student("S1", outstanding_dues=100)
    course = Course("CS201", 3, 30)

    register_course(student, course)

    assert student.current_credits == 0
    assert student.registered_courses == set()
    assert course.enrolled == 0


def test_withdraw_successfully():
    student = Student(
        "S1",
        current_credits=3,
        registered_courses={"CS201"}
    )
    course = Course("CS201", 3, 30, enrolled=1)

    result = withdraw_course(student, course)

    assert result is True
    assert "CS201" not in student.registered_courses
    assert student.current_credits == 0
    assert course.enrolled == 0


def test_withdraw_unregistered_course():
    student = Student("S1")
    course = Course("CS201", 3, 30)

    result = withdraw_course(student, course)

    assert result is False
    assert student.current_credits == 0
    assert course.enrolled == 0


# ==============================
# INPUT VALIDATION
# ==============================

def test_negative_dues():
    student = Student("S1", outstanding_dues=-1)
    course = Course("CS201", 3, 30)

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


def test_invalid_capacity():
    student = Student("S1")
    course = Course("CS201", 3, 0)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_enrolled_greater_than_capacity():
    student = Student("S1")
    course = Course("CS201", 3, 30, enrolled=31)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_dues_validation_priority():
    student = Student("S1", outstanding_dues=-1)
    course = Course("CS201", 3, 0)

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)

        # ==============================
# ADDITIONAL REQUIREMENT COVERAGE
# ==============================

def test_registration_decision_does_not_mutate_state():
    student = Student("S1", current_credits=5)
    course = Course("CS201", 3, 30, enrolled=10)

    original_student = (
        student.current_credits,
        student.outstanding_dues,
        student.registered_courses.copy(),
        student.completed_courses.copy()
    )

    original_course = (
        course.enrolled,
        course.waitlist.copy()
    )

    registration_decision(student, course)

    assert (
        student.current_credits,
        student.outstanding_dues,
        student.registered_courses,
        student.completed_courses
    ) == original_student

    assert (
        course.enrolled,
        course.waitlist
    ) == original_course


def test_credit_limit_priority_over_full_course():
    student = Student("S1", current_credits=16)
    course = Course("CS201", 3, 30, enrolled=30)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


def test_invalid_current_credits_priority():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 5)


def test_failed_withdrawal_preserves_all_state():
    student = Student(
        "S1",
        current_credits=6,
        registered_courses={"CS101"}
    )

    course = Course(
        "CS201", 3, 30,
        enrolled=10,
        waitlist=["S2"]
    )

    original_registered = student.registered_courses.copy()
    original_waitlist = course.waitlist.copy()

    result = withdraw_course(student, course)

    assert result is False
    assert student.current_credits == 6
    assert student.registered_courses == original_registered
    assert course.enrolled == 10
    assert course.waitlist == original_waitlist


def test_failed_registration_preserves_all_state():
    student = Student(
        "S1",
        outstanding_dues=100,
        current_credits=5,
        registered_courses={"CS101"}
    )

    course = Course(
        "CS201", 3, 30,
        enrolled=10,
        waitlist=["S2"]
    )

    original_registered = student.registered_courses.copy()
    original_waitlist = course.waitlist.copy()

    result = register_course(student, course)

    assert result == "DUES_BLOCK"
    assert student.current_credits == 5
    assert student.registered_courses == original_registered
    assert course.enrolled == 10
    assert course.waitlist == original_waitlist
