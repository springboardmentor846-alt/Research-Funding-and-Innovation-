def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def check_funding_eligibility(profile, funding):

    eligible = True
    reasons = []
    warnings = []

    # ==========================================================
    # 1. QUALIFICATION CHECK
    # ==========================================================

    required_qualification = normalize(
        funding.qualification
    )

    researcher_qualification = normalize(
        profile.highest_qualification
    )

    if required_qualification:

        if not researcher_qualification:

            warnings.append(
                "Researcher qualification is not available "
                "in the research profile."
            )

        else:

            required_parts = [
                part.strip()
                for part in required_qualification.split(",")
                if part.strip()
            ]

            qualification_match = any(
                part in researcher_qualification
                or researcher_qualification in part
                for part in required_parts
            )

            if not qualification_match:

                eligible = False

                reasons.append(
                    f"Required qualification: "
                    f"{funding.qualification}"
                )

    # ==========================================================
    # 2. CAREER STAGE CHECK
    # ==========================================================

    required_stage = normalize(
        funding.career_stage
    )

    researcher_position = normalize(
        profile.current_position
    )

    if required_stage:

        if not researcher_position:

            warnings.append(
                "Current position is not available "
                "in the research profile."
            )

        else:

            stages = [
                stage.strip()
                for stage in required_stage.split(",")
                if stage.strip()
            ]

            stage_match = any(
                stage in researcher_position
                or researcher_position in stage
                for stage in stages
            )

            if not stage_match:

                warnings.append(
                    f"Career-stage requirement should be verified: "
                    f"{funding.career_stage}"
                )

    # ==========================================================
    # 3. COUNTRY / INTERNATIONAL ELIGIBILITY
    # ==========================================================

    if (
        funding.country
        and not funding.international_applicants_allowed
    ):

        warnings.append(
            f"This opportunity may be restricted to "
            f"applicants from {funding.country}."
        )

    if funding.eligible_countries:

        warnings.append(
            f"Eligible countries: "
            f"{funding.eligible_countries}"
        )

    # ==========================================================
    # 4. EXPERIENCE REQUIREMENT
    # ==========================================================

    if funding.experience_required:

        warnings.append(
            f"This opportunity requires or may require "
            f"{funding.experience_required} years of experience."
        )

    # ==========================================================
    # 5. FINAL ELIGIBILITY STATUS
    # ==========================================================

    if reasons:

        status = "Not Eligible"

    elif warnings:

        status = "Potentially Eligible"

    else:

        status = "Eligible"

    return {
        "eligible": eligible,
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
    }