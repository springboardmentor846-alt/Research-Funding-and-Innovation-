from collections import Counter

from sqlalchemy import select

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.lens_service import search_patents

from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea


# =========================================================
# HUMAN-READABLE PATENT JURISDICTION NAMES
# =========================================================

JURISDICTION_NAMES = {

    "US": "United States",
    "CN": "China",
    "JP": "Japan",
    "KR": "South Korea",
    "IN": "India",
    "GB": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "CA": "Canada",
    "AU": "Australia",
    "RU": "Russia",
    "TW": "Taiwan",
    "ZA": "South Africa",
    "BR": "Brazil",
    "MX": "Mexico",
    "SG": "Singapore",
    "NZ": "New Zealand",
    "IT": "Italy",
    "ES": "Spain",
    "NL": "Netherlands",
    "SE": "Sweden",
    "CH": "Switzerland",
    "AT": "Austria",
    "BE": "Belgium",
    "DK": "Denmark",
    "FI": "Finland",
    "NO": "Norway",

    # International / regional patent authorities

    "WO": "WIPO / International",
    "EP": "European Patent Office",
}


# =========================================================
# BROAD CPC TECHNOLOGY SECTIONS
# =========================================================

CPC_SECTIONS = {

    "A": "Human Necessities",

    "B": "Performing Operations & Transporting",

    "C": "Chemistry & Metallurgy",

    "D": "Textiles & Paper",

    "E": "Fixed Constructions",

    "F": "Mechanical Engineering",

    "G": "Physics",

    "H": "Electricity",

    "Y": "Emerging / Cross-sectional Technologies",
}


# =========================================================
# HELPER:
# SAFELY GET TEXT VALUE FROM DATABASE MODEL
# =========================================================

def get_model_text(
    obj,
    possible_fields
):

    for field in possible_fields:

        value = getattr(
            obj,
            field,
            None
        )

        if value:

            return str(value)

    return ""


# =========================================================
# BUILD RESEARCHER TEXT
# =========================================================

def build_researcher_text(
    profile,
    domains,
    keywords,
    technologies
):

    text_parts = []


    # -----------------------------------------------------
    # PROFILE INFORMATION
    # -----------------------------------------------------

    if profile:

        if profile.bio:

            text_parts.append(
                profile.bio
            )


        if profile.highest_qualification:

            text_parts.append(
                profile.highest_qualification
            )


        if profile.current_position:

            text_parts.append(
                profile.current_position
            )


        if profile.organization_name:

            text_parts.append(
                profile.organization_name
            )


    # -----------------------------------------------------
    # RESEARCH DOMAINS
    # -----------------------------------------------------

    for domain in domains:

        value = get_model_text(

            domain,

            [
                "domain_name",
                "name",
                "domain"
            ]

        )

        if value:

            text_parts.append(
                value
            )


    # -----------------------------------------------------
    # RESEARCH KEYWORDS
    # -----------------------------------------------------

    for keyword in keywords:

        value = get_model_text(

            keyword,

            [
                "keyword",
                "keyword_name",
                "name"
            ]

        )

        if value:

            text_parts.append(
                value
            )


    # -----------------------------------------------------
    # TECHNOLOGY AREAS
    # -----------------------------------------------------

    for technology in technologies:

        value = get_model_text(

            technology,

            [
                "technology_name",
                "technology_area",
                "name"
            ]

        )

        if value:

            text_parts.append(
                value
            )


    return " ".join(
        text_parts
    )


# =========================================================
# CALCULATE SEMANTIC SIMILARITY
# =========================================================

def calculate_similarity(
    researcher_text,
    patent_text
):

    if not researcher_text:

        return 0.0


    if not patent_text:

        return 0.0


    try:

        vectorizer = TfidfVectorizer(

            stop_words="english"

        )


        vectors = vectorizer.fit_transform(

            [
                researcher_text,
                patent_text
            ]

        )


        similarity = cosine_similarity(

            vectors[0:1],

            vectors[1:2]

        )[0][0]


        return float(
            similarity
        )


    except ValueError:

        return 0.0


# =========================================================
# MAIN PATENT LANDSCAPE SERVICE
# =========================================================

def patent_landscape(
    query: str,
    db,
    current_user
):


    # =====================================================
    # 1. GET CURRENT RESEARCHER PROFILE
    # =====================================================

    profile = db.scalar(

        select(
            ResearchProfile
        ).where(

            ResearchProfile.user_id
            == current_user.id

        )

    )


    domains = []

    keywords = []

    technologies = []

    researcher_text = ""


    # =====================================================
    # 2. LOAD RESEARCHER INFORMATION
    # =====================================================

    if profile:


        # -------------------------------------------------
        # DOMAINS
        # -------------------------------------------------

        domains = db.scalars(

            select(
                ResearchDomain
            ).where(

                ResearchDomain.research_profile_id
                == profile.id

            )

        ).all()


        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        keywords = db.scalars(

            select(
                ResearchKeyword
            ).where(

                ResearchKeyword.research_profile_id
                == profile.id

            )

        ).all()


        # -------------------------------------------------
        # TECHNOLOGY AREAS
        # -------------------------------------------------

        technologies = db.scalars(

            select(
                TechnologyArea
            ).where(

                TechnologyArea.research_profile_id
                == profile.id

            )

        ).all()


        # -------------------------------------------------
        # BUILD RESEARCHER TEXT
        # -------------------------------------------------

        researcher_text = build_researcher_text(

            profile,
            domains,
            keywords,
            technologies

        )


    # =====================================================
    # 3. SEARCH LENS PATENTS
    # =====================================================

    response = search_patents(

        query=query,

        size=100

    )


    patents = response.get(

        "data",

        []

    )


    # =====================================================
    # 4. ANALYTICS COUNTERS
    # =====================================================

    jurisdiction_counter = Counter()

    status_counter = Counter()

    year_counter = Counter()

    applicant_counter = Counter()

    cpc_counter = Counter()

    cluster_counter = Counter()


    # Personalized patents

    relevant_patents = []


    # =====================================================
    # 5. PROCESS EVERY PATENT
    # =====================================================

    for patent in patents:


        # =================================================
        # JURISDICTION
        # =================================================

        jurisdiction = patent.get(

            "jurisdiction"

        )


        if jurisdiction:

            jurisdiction_counter[
                jurisdiction
            ] += 1


        # =================================================
        # LEGAL STATUS
        # =================================================

        legal = patent.get(

            "legal_status"

        ) or {}


        status = legal.get(

            "patent_status"

        )


        if status:

            status_counter[
                status
            ] += 1


        # =================================================
        # BIBLIOGRAPHIC DATA
        # =================================================

        biblio = patent.get(

            "biblio"

        ) or {}


        # =================================================
        # PUBLICATION INFORMATION
        # =================================================

        publication_reference = (

            biblio.get(
                "publication_reference"
            )

            or {}

        )


        publication_number = (

            publication_reference.get(
                "doc_number"
            )

            or

            publication_reference.get(
                "document_id"
            )

        )


        publication_date = (

            publication_reference.get(
                "date"
            )

        )


        # =================================================
        # FILING / PUBLICATION TREND
        # =================================================

        if publication_date:

            year_counter[
                publication_date[:4]
            ] += 1


        # =================================================
        # APPLICANTS
        # =================================================

        parties = (

            biblio.get(
                "parties"
            )

            or {}

        )


        applicants_data = (

            parties.get(
                "applicants"
            )

            or []

        )


        patent_applicants = []


        for applicant in applicants_data:


            applicant_name = (

                applicant.get(
                    "extracted_name"
                )

                or {}

            ).get(
                "value"
            )


            if applicant_name:


                applicant_counter[
                    applicant_name
                ] += 1


                patent_applicants.append(

                    applicant_name

                )


        # =================================================
        # CPC CLASSIFICATIONS
        # =================================================

        classifications_cpc = (

            biblio.get(
                "classifications_cpc"
            )

            or {}

        )


        classifications = (

            classifications_cpc.get(
                "classifications"
            )

            or []

        )


        patent_cpcs = []


        for classification in classifications:


            symbol = classification.get(

                "symbol"

            )


            if symbol:


                # -----------------------------------------
                # Count CPC
                # -----------------------------------------

                cpc_counter[
                    symbol
                ] += 1


                patent_cpcs.append(

                    symbol

                )


                # -----------------------------------------
                # Broad CPC technology cluster
                # -----------------------------------------

                section_code = symbol[0]


                section_name = CPC_SECTIONS.get(

                    section_code,

                    "Other Technologies"

                )


                cluster_counter[
                    section_name
                ] += 1


        # =================================================
        # PATENT TITLE
        # =================================================

        invention_title = (

            biblio.get(
                "invention_title"
            )

            or []

        )


        title = None


        # -------------------------------------------------
        # Title is a list
        # -------------------------------------------------

        if isinstance(
            invention_title,
            list
        ):


            # Prefer English title

            for title_item in invention_title:


                if isinstance(
                    title_item,
                    dict
                ):


                    if (

                        title_item.get(
                            "lang"
                        )
                        == "en"

                        and

                        title_item.get(
                            "text"
                        )

                    ):

                        title = title_item.get(

                            "text"

                        )

                        break


                    if (

                        title_item.get(
                            "language"
                        )
                        == "en"

                        and

                        title_item.get(
                            "value"
                        )

                    ):

                        title = title_item.get(

                            "value"

                        )

                        break


            # ---------------------------------------------
            # If no English title exists,
            # use first available title
            # ---------------------------------------------

            if (

                not title

                and

                invention_title

            ):


                first_title = (

                    invention_title[0]

                )


                if isinstance(
                    first_title,
                    dict
                ):

                    title = (

                        first_title.get(
                            "text"
                        )

                        or

                        first_title.get(
                            "value"
                        )

                    )


        # -------------------------------------------------
        # Title is directly a string
        # -------------------------------------------------

        elif isinstance(
            invention_title,
            str
        ):

            title = invention_title


        # =================================================
        # PATENT ABSTRACT
        # =================================================

        abstract_data = (

            biblio.get(
                "abstract"
            )

            or

            patent.get(
                "abstract"
            )

            or []

        )


        abstract_text = ""


        # -------------------------------------------------
        # Abstract directly returned as string
        # -------------------------------------------------

        if isinstance(
            abstract_data,
            str
        ):

            abstract_text = abstract_data


        # -------------------------------------------------
        # Abstract returned as list
        # -------------------------------------------------

        elif isinstance(
            abstract_data,
            list
        ):


            # First try English abstract

            for abstract_item in abstract_data:


                if isinstance(
                    abstract_item,
                    dict
                ):


                    language = (

                        abstract_item.get(
                            "lang"
                        )

                        or

                        abstract_item.get(
                            "language"
                        )

                    )


                    text = (

                        abstract_item.get(
                            "text"
                        )

                        or

                        abstract_item.get(
                            "value"
                        )

                    )


                    if (

                        language == "en"

                        and

                        text

                    ):

                        abstract_text = text

                        break


            # ---------------------------------------------
            # If English abstract wasn't found,
            # take first available abstract
            # ---------------------------------------------

            if not abstract_text:


                for abstract_item in abstract_data:


                    if isinstance(
                        abstract_item,
                        dict
                    ):


                        text = (

                            abstract_item.get(
                                "text"
                            )

                            or

                            abstract_item.get(
                                "value"
                            )

                        )


                        if text:

                            abstract_text = text

                            break


        # -------------------------------------------------
        # Abstract returned as dictionary
        # -------------------------------------------------

        elif isinstance(
            abstract_data,
            dict
        ):

            abstract_text = (

                abstract_data.get(
                    "text"
                )

                or

                abstract_data.get(
                    "value"
                )

                or ""

            )


        # =================================================
        # BUILD PATENT TEXT
        # =================================================

        patent_text_parts = []


        if title:

            patent_text_parts.append(

                title

            )


        if abstract_text:

            patent_text_parts.append(

                abstract_text

            )


        # CPC codes are included as supporting
        # technical classification information

        if patent_cpcs:

            patent_text_parts.extend(

                patent_cpcs

            )


        patent_text = " ".join(

            patent_text_parts

        )


        # =================================================
        # PERSONALIZED RELEVANCE CALCULATION
        # =================================================

        similarity = 0.0


        if (

            researcher_text

            and

            patent_text

        ):

            similarity = calculate_similarity(

                researcher_text,

                patent_text

            )


        relevance_score = round(

            similarity * 100,

            2

        )


        # =================================================
        # STORE RELEVANT PATENT INFORMATION
        # =================================================

        relevant_patents.append({


            "title":

                title
                or "Title unavailable",


            "publication_number":

                publication_number,


            "publication_date":

                publication_date,


            "jurisdiction":

                jurisdiction,


            "jurisdiction_name":

                JURISDICTION_NAMES.get(

                    jurisdiction,

                    jurisdiction

                )
                if jurisdiction
                else None,


            "applicants":

                patent_applicants[:3],


            "cpc_codes":

                patent_cpcs[:5],


            "status":

                status,


            "relevance_score":

                relevance_score

        })


    # =====================================================
    # 6. SORT PERSONALIZED PATENTS
    # =====================================================

    relevant_patents.sort(

        key=lambda item:

            item[
                "relevance_score"
            ],

        reverse=True

    )


    # =====================================================
    # 7. BUILD JURISDICTION DISTRIBUTION
    # =====================================================

    jurisdiction_distribution = []


    for (

        code,

        count

    ) in jurisdiction_counter.most_common(10):


        jurisdiction_distribution.append({


            "code":

                code,


            "name":

                JURISDICTION_NAMES.get(

                    code,

                    code

                ),


            "count":

                count

        })


    # =====================================================
    # 8. GENERATE INSIGHTS
    # =====================================================

    insights = []


    # -----------------------------------------------------
    # Top patent jurisdiction
    # -----------------------------------------------------

    if jurisdiction_counter:


        top_code = (

            jurisdiction_counter
            .most_common(1)[0][0]

        )


        top_name = JURISDICTION_NAMES.get(

            top_code,

            top_code

        )


        insights.append(

            f"Top patent filing jurisdiction: "
            f"{top_name} ({top_code})"

        )


    # -----------------------------------------------------
    # Most active organization
    # -----------------------------------------------------

    if applicant_counter:


        top_applicant = (

            applicant_counter
            .most_common(1)[0][0]

        )


        insights.append(

            f"Most active organization: "
            f"{top_applicant}"

        )


    # -----------------------------------------------------
    # Most common CPC class
    # -----------------------------------------------------

    if cpc_counter:


        top_cpc = (

            cpc_counter
            .most_common(1)[0][0]

        )


        insights.append(

            f"Most common CPC class: "
            f"{top_cpc}"

        )


    # =====================================================
    # 9. BUILD INNOVATION MAP
    # =====================================================

    total_cluster_occurrences = sum(

        cluster_counter.values()

    )


    innovation_map = []


    for (

        cluster,

        count

    ) in cluster_counter.most_common():


        if total_cluster_occurrences > 0:

            share = round(

                (
                    count
                    /
                    total_cluster_occurrences
                )
                * 100,

                2

            )

        else:

            share = 0


        innovation_map.append({


            "technology_cluster":

                cluster,


            "classification_occurrences":

                count,


            "share_percentage":

                share

        })


    # =====================================================
    # 10. API RESPONSE
    # =====================================================

    return {


        "query":

            query,


        # -------------------------------------------------
        # Whether profile-based matching was available
        # -------------------------------------------------

        "personalized_relevance":

            bool(
                profile
                and researcher_text.strip()
            ),


        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        "summary": {


            "total_patents":

                len(patents),


            "countries":

                len(
                    jurisdiction_counter
                ),


            "organizations":

                len(
                    applicant_counter
                ),


            "technology_classes":

                len(
                    cpc_counter
                )

        },


        # -------------------------------------------------
        # Country distribution
        # -------------------------------------------------

        "country_distribution":

            jurisdiction_distribution,


        # -------------------------------------------------
        # Status distribution
        # -------------------------------------------------

        "status_distribution":

            dict(
                status_counter
            ),


        # -------------------------------------------------
        # Filing trends
        # -------------------------------------------------

        "filing_trends":

            dict(

                sorted(

                    year_counter.items()

                )

            ),


        # -------------------------------------------------
        # Top organizations
        # -------------------------------------------------

        "top_applicants":

            dict(

                applicant_counter
                .most_common(10)

            ),


        # -------------------------------------------------
        # CPC classes
        # -------------------------------------------------

        "technology_classes":

            dict(

                cpc_counter
                .most_common(10)

            ),


        # -------------------------------------------------
        # Patent technology clusters
        # -------------------------------------------------

        "patent_clusters":

            dict(

                cluster_counter
                .most_common()

            ),


        # -------------------------------------------------
        # PERSONALIZED RELEVANT PATENTS
        # -------------------------------------------------

        "relevant_patents":

            relevant_patents[:20],


        # -------------------------------------------------
        # Innovation mapping
        # -------------------------------------------------

        "innovation_map":

            innovation_map,


        # -------------------------------------------------
        # Insights
        # -------------------------------------------------

        "insights":

            insights

    }