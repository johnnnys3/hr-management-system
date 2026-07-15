# Research Brief: Ghana's Data Protection Act, 2012 (Act 843)

**Human Resource Management System**

| | |
|---|---|
| Version | 1.0 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | 2026-07-15 |
| Status | Informational. Not a controlled deliverable. **Not legal advice** |
| Sources accessed | 2026-07-15 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | 2026-07-15 | Initial brief. Researched against the text of Act 843, L.I. 2512, and the draft Data Protection Bill, 2025, to scope the legal question ADR-0009's decision rule refers to counsel. Resolves nothing; TBD-003 remains open | 1.0 |

---

## 1. Introduction

### 1.1 Purpose

This brief assembles what Ghana's Data Protection Act, 2012 (Act 843) **says**, on four questions bearing on this system, so that a conversation with qualified Ghanaian counsel is shorter and better scoped than it would otherwise be.

It exists because ADR-0009 defers the hosting target and states a decision rule whose first condition is written confirmation from counsel on Act 843 obligations — "specifically, **whether the Act restricts transfer of that data outside Ghana, on what test, and what a lawful transfer requires**". That question is put to counsel, not answered here. This brief's contribution is to narrow it: to establish which provisions counsel is being asked about, and to record which parts of the answer the statute supplies on its face and which parts it does not.

### 1.2 What this document is not

**This is not legal advice, and nothing in it may be read as legal advice.** `docs/02-project-plan.md` §8.1 records TBD-003 as *open by decision* and §8.2 records it among the eleven TBDs **not resolvable by this project**. SRS §6.3 requires that legal and regulatory requirements be confirmed with qualified legal professionals before go-live. This brief does not disturb any of that.

Specifically, this document:

- **does not recommend a hosting target**, and does not narrow the field of them;
- **does not state that TBD-003 is resolved.** It is open, and only counsel plus an operating organisation can close it;
- **does not satisfy any condition of ADR-0009's decision rule.** Condition 1 requires written confirmation *from qualified legal counsel*. This is not that, and a document written by the project about the project cannot become that;
- **does not interpret the Act.** Where applying a provision to this system requires judgement, the brief says so and stops.

The distinction between *what the statute says* and *what applying it requires* is load-bearing here and is carried in the structure: §§3–6 each separate **"What the Act says"** from **"What requires legal judgement"**, and §8 collects the latter into questions for counsel.

### 1.3 Intended audience

The project owner, when instructing counsel. Secondarily, any reader of ADR-0009 who wants to know what is behind its deferral.

### 1.4 Related documents

| Document | Relationship |
|---|---|
| `docs/adr/0009-containerised-deployment-with-deferred-hosting-target.md` | States the decision rule this brief feeds. §7 records where this brief bears on it |
| `docs/02-project-plan.md` §8.1, §8.3 | TBD-003, TBD-001, TBD-009; deployment blockage |
| `docs/01-srs.md` §6.3 | Requires confirmation by qualified professionals before go-live |
| `docs/01-srs.md` HRMS-NFR-012, HRMS-NFR-020, HRMS-NFR-035 | Condition 3 of ADR-0009's decision rule |

## 2. Sources and method

Primary sources only. Every claim below is cited to the instrument that owns it, by section or clause number.

| # | Source | Type | URL | Accessed |
|---|---|---|---|---|
| S1 | Data Protection Act, 2012 (Act 843), full text, 43pp | Primary — statute, hosted by NITA, a government agency | `https://nita.gov.gh/wp-content/uploads/2017/12/Data-Protection-Act-2012-Act-843.pdf` | 2026-07-15 |
| S2 | Fees and Charges (Miscellaneous Provisions) (Amendment) Regulations, 2025, **L.I. 2512**, pp. 280–281, item (vii) — the Data Protection Commission fee table | Primary — Legislative Instrument, hosted by the DPC | `https://dataprotection.org.gh/wp-content/uploads/2026/02/DPC-NEW-FEES.pdf` | 2026-07-15 |
| S3 | Data Protection Commission, *Registration* | Primary — regulator's own guidance | `https://dataprotection.org.gh/registration/` | 2026-07-15 |
| S4 | Data Protection Bill, 2025, draft for public consultation, 82pp | Primary — draft bill, hosted by the DPC. **Not law** | `https://dataprotection.org.gh/wp-content/uploads/2025/11/DATA_PROTECTION_BILL1_DRAFT-1.pdf` | 2026-07-15 |
| S5 | Ghana News Agency, "Govt to introduce new Data Protection Bill…", 2026-03-02 | Secondary — reporting a minister's statement. Used **only** for the Bill's status | `https://gna.org.gh/2026/03/govt-to-introduce-new-data-protection-bill-to-regulate-ai-cross-border-data-flows/` | 2026-07-15 |

**Method and its limits.** S1 was read in full rather than searched, so statements below that the Act is *silent* on something are made against the whole text and not against a keyword. Law-firm commentary and secondary summaries were deliberately excluded from the substance; where a claim rests on one it is marked **[UNVERIFIED]** and the reason is given.

**Two claims are marked [UNVERIFIED] and neither is repaired below:**

1. **The cedi value of a penalty unit.** Act 843 states penalties in penalty units (§3.4). Their value is set by the Fines (Penalty Units) Act, 2000 (Act 572), whose text could not be retrieved from a primary source at the access date — the Parliament of Ghana repository redirected away from the document, and two other hosts refused the request. Secondary sources give GH¢12.00 per penalty unit. **That figure is not verified against Act 572 and is not relied on here.** It is recorded only to show what was looked for and not found. ADR-0009 already holds that penalty magnitude is not load-bearing for the deferral; this brief does not make it load-bearing by supplying a number it cannot source.
2. **Act 843's commencement date.** s.99 provides that "The Minister shall specify the date when this Act shall come into force by publication in the Gazette", and the text records "Date of Gazette notification: 18th May, 2012" (S1, s.99). Secondary sources state the Act came into force on 16 October 2012. **The commencement date is not verified against a primary source.** It does not affect any conclusion here, but it is a date counsel may need for the transitional provision at s.97(2).

**Fees are volatile.** The figures at §3.3 are as at **2026-07-15** and are the product of an amendment made in 2025. They should be re-checked at the point of use, not read forward from this document.

## 3. Question 1 — Registration

### 3.1 What the Act says: who must register, and what triggers it

The obligation is stated three times, in three places, and is unconditional in all three.

> **s.27(1)** "A data controller who intends to process personal data shall register with the Commission."

> **s.46(3)** "A data controller shall register with the Commission."

> **s.53** "A data controller who has not been registered under this Act shall not process personal data."

A **data controller** is defined at s.96 as "a person who either alone, jointly with other persons or in common with other persons or as a statutory duty determines the purposes for and the manner in which personal data is processed or is to be processed". An organisation running this HRMS over its own employees' records would determine both the purposes and the manner, and so would fall within that definition on its face.

**There is no threshold.** The Act sets no minimum headcount, turnover, or data volume below which registration is not required, and no small-organisation exemption. The trigger in s.27(1) is the *intention to process personal data*. The exemptions at ss.60–74 are subject-matter exemptions — national security, crime and taxation, journalism, domestic purposes, examination scripts, and similar — and none of them is an exemption for a small employer processing its own employees' records.

**Registration is per-purpose in its entries.** s.47(3): "Where a data controller intends to keep personal data for two or more purposes the Commission shall make separate entries for each purpose in the Register."

**Note a discrepancy in this repository.** ADR-0009 and `docs/02-project-plan.md` §8.3 both cite the registration obligation to **s.27(1)** alone. That citation is correct but incomplete: s.27(1) creates the duty, while the *machinery* — the Register, the application, the particulars, refusal, grant, renewal, cancellation, the prohibition on unregistered processing, and the offence — is at **ss.46–56**, and the deadline is at **s.97**. A reader following ADR-0009's citation to s.27 alone would find the duty and none of the mechanics, and would in particular not find the 20-day deadline at s.97(1) (§6.1 below). This is a citation-completeness point, not an error, and it does not change ADR-0009's decision.

### 3.2 What the Act says: what registration requires

s.47(1) requires an application in writing furnishing ten particulars. Four bear directly on this system:

> **s.47(1)(c)** "a description of the personal data to be processed and the category of persons whose personal data are to be collected;"
>
> **s.47(1)(d)** "an indication as to whether the applicant holds or is likely to hold special personal data;"
>
> **s.47(1)(g)** "the name or description of the country to which the appli\[c\]ant may transfer the data;"
>
> **s.47(1)(i)** "a general description of measures to be taken to secure the data;"

s.47(1)(g) is the provision that ties registration to hosting, and §4 takes it up.

The Commission **shall not** grant registration where "the appropriate safeguards for the protection of the privacy of the data subject have not been provided by the data controller" (s.48(1)(b)), or where the particulars are insufficient (s.48(1)(a)), or where "in the opinion of the Commission, the person making the application… does not merit the grant" (s.48(1)(c)). Refusal must be given in writing with reasons within fourteen days, is subject to judicial review in the High Court, and does not bar re-application (s.48(2)–(3)).

Changes to registered particulars must be notified within fourteen days (s.55).

### 3.3 What the Act and L.I. 2512 say: cost and renewal cycle

**Renewal cycle — s.50:** "A registration shall be renewed every two years." The DPC's own guidance adds that its portal permits renewal from three months and six weeks before expiry and up to 7 days after expiration (S3).

**Cost.** The Act does not set fees. It defers them:

> **s.49(2)** "The applicant shall pay the prescribed fee upon registration."
>
> **s.59** "The Minister may by Regulations prescribe fees for the purpose of sections 49, 50 and 54."

The fees currently published by the Commission are prescribed by **L.I. 2512**, the Fees and Charges (Miscellaneous Provisions) (Amendment) Regulations, 2025, which at item (vii) substitutes a new fee table for the Data Protection Commission (S2, pp. 280–281). The registration fees, verbatim, **as at 2026-07-15**:

| Revenue item (L.I. 2512 wording) | Approved fee (GH¢) |
|---|---|
| **REGISTRATION FEES** | |
| Specialised Industries | 5,000.00 |
| **Large Data Controllers / Processors** — Primary Criterion: "data controllers or data processors with annual turnover of five million Ghana Cedis (GH¢5 million) and above or minimum of 250 members or staff." | 2,340.00 |
| Large — Secondary criterion: "specialist industries no matter the turnover" — (i) upstream and midstream petroleum companies, (ii) telecommunication companies or operators (class 1 licence operators), (iii) banking/financial institutions, (iv) credit bureaus, (v) insurance companies, (vi) mining companies, except quarries | 2,340.00 |
| Large — "Members of groups of companies, no matter the turnover, which has one associate or subsidiary qualifying as a large data controller or data processor" | 2,340.00 |
| **Medium Data Controllers or Processors** — "annual turnover of above ninety thousand Ghana Cedis (GH¢90,000.00) but below 5 million or a maximum of 50 members of staff or Customers not above 249" | 1,170.00 |
| **Small Data Controllers / Processors** — "annual turnover of ninety thousand Ghana Cedis (GH¢ 90,000.00) and below a maximum of 50 members of staff or customers" | 156.00 |
| Replacement of certificates | 38.00 |

**Which band this system's controller falls into cannot be determined**, because TBD-001 leaves no organisation, and every band in L.I. 2512 is keyed to turnover, staff count, customer count, or industry. The table is recorded so that the question can be priced once an organisation exists — not so that a figure can be carried forward now.

**Three gaps in the fee position, stated rather than filled:**

1. **No renewal fee is itemised.** s.59 empowers the Minister to prescribe fees for s.50 (renewal) as well as s.49 (registration), but the DPC table at S2 has a "REGISTRATION FEES" heading and no renewal line. Whether renewal is charged at the registration rate, at some other rate, or under a different instrument is **not determinable from L.I. 2512's DPC extract**.
2. **The band criteria overlap and are internally inconsistent.** "Medium" is defined as turnover above GH¢90,000 but below 5 million **or** "a maximum of 50 members of staff", while "Small" is turnover of GH¢90,000 and below **and** a maximum of 50 staff or customers. An entity with 40 staff and GH¢2m turnover satisfies a limb of both. The instrument does not state whether the criteria are conjunctive or disjunctive, or which governs on conflict.
3. **The instrument's relationship to s.59 is not established here.** L.I. 2512 is a general fees-and-charges amendment covering multiple ministries and agencies, not an instrument made under Act 843 s.59 on its face. Whether it is the "Regulations" s.59 contemplates is a question this brief does not answer.

### 3.4 What the Act says: penalties for operating unregistered

> **s.56** "A person who fails to register as a data controller but processes personal data commits an offence and is liable on summary conviction to a fine of not more than two hundred and fifty penalty units or a term of imprisonment of not more than two years or to both."

Other penalties in the registration chain:

| Provision | Conduct | Maximum penalty |
|---|---|---|
| s.47(2) | Knowingly supplying false information in support of a registration application | 150 penalty units, or 1 year imprisonment, or both |
| s.56 | Failing to register but processing personal data | 250 penalty units, or 2 years imprisonment, or both |
| s.57(6) | Carrying on assessable processing in contravention of s.57 | 250 penalty units, or 2 years imprisonment, or both |
| s.80(1) | Failing to comply with an enforcement notice or information notice | 150 penalty units, or 1 year imprisonment, or both |
| s.95 (general penalty) | An offence under the Act "in respect of which a penalty is not specified" | 5,000 penalty units, or 10 years imprisonment, or both |

Beyond the criminal penalties, the Commission may serve an **enforcement notice** (s.75), may **cancel a registration for good cause** (s.52) — "good cause" being defined at s.96 as "any failure to comply with or a violation of any of the data protection principles, enforcement or other notices issued by the Commission" — and a data subject who "suffers damage or distress through the contravention" may claim **compensation** (s.43).

**On magnitude, this brief follows ADR-0009 and does not quantify.** The Act expresses these penalties in penalty units, and the cedi value of a penalty unit is **[UNVERIFIED]** per §2. ADR-0009 has already withdrawn one penalty figure stated in a shape the Act does not use, and records that "the magnitude of the penalty is not load-bearing". Supplying a number here that cannot be sourced would repeat exactly the defect that record corrected.

### 3.5 What requires legal judgement

- Whether the organisation, once it exists, is a data controller, a data processor, or both on these facts — and whether any of ss.60–74 reaches any part of an HRMS.
- Which L.I. 2512 band applies, given the overlap at §3.3(2).
- Whether the renewal fee is the registration fee (§3.3(1)).
- **Whether an unregistered controller that processes personal data is exposed under s.56 only, or also under s.95.** s.53 prohibits unregistered processing but does not itself say that contravening it "commits an offence", and s.95 applies to an offence "in respect of which a penalty is not specified". Whether s.53 creates a distinct s.95 offence carrying 5,000 penalty units and 10 years, or whether s.56 is the exhaustive sanction for the same conduct at 250 penalty units and 2 years, is a question of construction — and the two readings differ by a factor of twenty on the fine and five on the custodial term. **The Act does not resolve this on its face and neither does this brief.**
- Whether any HRMS processing is **assessable processing** under s.57. This turns on an Executive Instrument made by the Minister, which was not located at the access date. If it applies, processing may not begin until 28 days after notification (s.57(5)) — a lead time bearing on any deployment schedule.

## 4. Question 2 — Hosting location

This is the section ADR-0009's decision rule turns on, and the finding is the most consequential in the brief.

### 4.1 What the Act says: there is no general restriction on hosting outside Ghana

**Act 843 contains no provision restricting where personal data may be physically hosted, and no general restriction on transferring personal data out of Ghana.** This is stated against the full text of the Act (S1, read in full, 43pp), and against its arrangement of sections: there is **no** section headed transfer, cross-border transfer, foreign transfer, export, adequacy, or data localisation, and no such provision appears under any other heading. The Act has no eighth-principle analogue to the kind of transfer restriction found in GDPR-lineage statutes.

The Act uses the word "transfer" in relation to personal data in exactly **one** operative place, s.47(1)(g), and it is a **disclosure particular of the registration application**, not a restriction:

> **s.47(1)(g)** "the name or description of the country to which the appli\[c\]ant may transfer the data;"

The controller must **tell** the Commission where data may go. The Act does not, in this section or any other, make the transfer conditional on where that is, on the destination's level of protection, or on the Commission's approval.

**This is consistent with ADR-0009 as it now stands, and confirms its correction.** That record withdrew, as unsupported, an earlier claim that Act 843 "restricts transfer of personal data outside Ghana unless the destination provides an adequate level of protection", and observed that no adequacy regime of the GDPR kind exists in the Act. **Reading the Act in full supports the withdrawal.** ADR-0009 was right both to withdraw the claim and to decline to replace it with a better-sounding one, and this brief adds only that the withdrawn sentence was not merely uncited but describes machinery the statute does not contain.

**ADR-0009's careful phrasing is also vindicated.** That record says: "**What follows is that the position is open, not that it is permissive.**" That remains exactly right, and §4.4 explains why the absence of a prohibition is not a permission.

### 4.2 What the Act says: the provisions that *do* touch foreign processing

Three provisions bear on data crossing Ghana's border. **None of them restricts outbound hosting**, and two of them run the opposite way to the concern in ADR-0009.

**(a) s.18(2) — inbound only.** This is the provision most likely to be mistaken for a transfer rule. It is not one, and it points *into* Ghana, not out:

> **s.18(2)** "A data controller or processor shall in respect of **foreign data subjects** ensure that personal data is processed in compliance with data protection legislation of the foreign jurisdiction of that subject **where personal data originating from that jurisdiction is sent to this country for processing**."

s.96 defines "**foreign data subject**" as "data subject information regulated by l\[a\]ws of a foreign jurisdiction **sent into Ghana from a foreign jurisdiction** wholly for processing purposes". This governs data *arriving* in Ghana for processing. It has no application to personal data of Ghanaian employees, which does not originate in a foreign jurisdiction, and no application to hosting that data abroad.

**(b) s.30(4) — the closest provision to the question, and it is an obligation, not a prohibition.** This is the single most relevant sentence in the Act for ADR-0009:

> **s.30(4)** "Where a data processor is **not domiciled in this country**, the data controller shall ensure that the data processor **complies with the relevant laws of this country**."

The Act's posture toward offshore processing is therefore, on its face, **extraterritorial extension rather than prohibition**: the controller may use a processor abroad, and must ensure that processor complies with Ghanaian law. Read with s.30(2) — "The processing of personal data for a data controller by a data processor shall be governed by a **written contract**" — and s.30(3), which requires that contract to oblige the processor to establish and maintain confidentiality and security measures, the Act's mechanism for offshore processing is **contractual and duty-based**, not permissive-list-based.

**(c) s.45(1) — the Act follows the data, not the server.** The Act applies where:

> **s.45(1)** "(a) the data controller is established in this country and the data is processed in this country, (b) the data controller is not established in this country but uses equipment or a data processor carrying on business in this country to process the data, or (c) **processing is in respect of information which originates partly or wholly from this country**."

Limb (c) is broad, and it is the limb that matters: personal data of Ghanaian employees originates in Ghana, so the Act reaches the processing **wherever it physically occurs**. A controller does not leave Act 843 by leaving Ghana. s.45(3) treats a body incorporated under Ghanaian law as established in the country, and s.45(2) requires a controller not incorporated in Ghana to register as an external company. s.45(4) excludes only data "which originates externally and merely transits through this country".

### 4.3 What the Act says: conditions that attach to hosting outside Ghana

The Act imposes no condition *of the form* "you may host abroad if X". What it does impose, and what would continue to bind wherever the data sits, is:

1. **Disclose the destination country at registration** (s.47(1)(g)), and notify changes within fourteen days (s.55). A change of hosting country is a change of registered particulars.
2. **Ensure a non-domiciled processor complies with Ghanaian law** (s.30(4)), under a **written contract** meeting s.30(2)–(3).
3. **All eight data protection principles continue to apply** (ss.17–26), because s.45(1)(c) attaches to the data's origin rather than to the processing location.
4. **Security measures under s.28 continue to apply** to data "in the possession or control of a person", a formula that is not territorial.
5. **The Commission may refuse registration** if "the appropriate safeguards for the protection of the privacy of the data subject have not been provided" (s.48(1)(b)). This is the widest discretion in the registration chain, and it is the provision through which a hosting arrangement could in practice be examined — **without any transfer rule being needed.** A destination the Commission regarded as unsafe could be met with refusal under s.48(1)(b) rather than with a transfer prohibition, because the Act gives the Commission the former and not the latter.

### 4.4 What requires legal judgement

**The absence of a prohibition is not a permission, and this brief does not present it as one.** Four things stand between "the Act contains no transfer restriction" and "hosting outside Ghana is lawful", and each is counsel's:

- **s.48(1)(b) and s.48(1)(c) are discretionary and broad.** Whether the Commission in practice treats offshore hosting as a safeguards question at registration — and on what view — is regulatory practice, not statutory text, and it is not discoverable from the Act. This is the practical route by which the answer could resemble a transfer restriction even though no transfer restriction exists.
- **s.30(4) may be harder to satisfy than to state.** "Ensure that the data processor complies with the relevant laws of this country" is an obligation of result on its face. Whether a controller can *ensure* that of a large foreign platform provider on standard non-negotiable terms — and what "the relevant laws of this country" comprehends — is a judgement about contracts and about the Act's reach that this project cannot make. **This, not any transfer rule, is the provision most likely to constrain a hosting choice.**
- **Sector law outside Act 843 was not surveyed.** This brief covers Act 843, L.I. 2512, and the draft Bill. Ghanaian law may restrict the location of payroll, tax, or pension records through instruments this brief did not look at — revenue law bearing on PAYE records, SSNIT law bearing on contribution records, companies law bearing on statutory books, or Bank of Ghana rules where a bank transfer file is involved (TBD-006). **The Act's silence on residency is not the legal system's silence on residency**, and a survey of Act 843 cannot establish the latter. This is a scoping limit of this brief, and it is stated because the temptation to read the finding at §4.1 more widely than it goes is the main risk this document creates.
- **The Bill would change the answer** (§4.5).

### 4.5 The Data Protection Bill, 2025 — and why it points the other way

**Status:** the Bill is **not law** and, as at the access date, has **not been introduced in Parliament**. It was published for public consultation by the Ministry of Communication, Digital Technology and Innovations in October–November 2025 (S4). The Minister stated in March 2026 that the government is still *developing* it for introduction (S5 — secondary, used only for status). It would repeal and replace Act 843 in its entirety.

ADR-0009 records the Bill as "reported to propose a more restrictive position, including a data localisation preference, transfer impact assessments, and Commission approval for high-risk transfers", and marks its contents "as reported rather than as established". **The draft text is available from the DPC and confirms all three limbs of that report.** ADR-0009 was right to hedge, and this brief upgrades the source from report to draft text — while noting that a draft is not an enactment and its clauses may not survive.

Quoting the draft (S4), and noting the drafting is rough in places:

> **cl. 96(1)** "Notwithstanding the opportunity to under a cross-border transfer personal data under subsection (3), a data controller shall **make reasonable efforts to localise data provided that data localisation does not impair its business or operations**."

> **cl. 96(2)** "There shall be **no requirement for a data controller to localise personal data unless**: (a) the personal data is critical to national defence, security and intelligence of the country; or (b) the personal data concern national identity ID systems and civil registration systems including voter databases (c) the personal data concerns **children's data, biometric data, health records and genetic data**."

> **cl. 96(4)** "A data controller shall transfer personal data outside Ghana **only if** the following conditions are met: (a) **the data subject has provided written, free, explicit and informed consent** to the proposed transfer after being informed of the possible risks involved; and (b) \[the transfer is necessary for a contract, legal claims, or vital interests…\]; and (c) **the transfer is authorised by the Authority where it involves large-scale data**, and in all cases, following an assessment that adequate safeguards… are in place, including appropriate contractual clauses and binding corporate rules or other mechanisms approved by the Authority."

> **cl. 97(4)** "A data controller that processes large-scale data where a data processing activity is likely to pose real risk to the rights and freedoms of a data subject, shall conduct a **Transfer Impact Assessment** on all data transfers in or outside the jurisdiction subject to the approval of the Authority."

**Three observations, each of which is a question rather than a conclusion:**

1. **The direction of travel is toward restriction, from a baseline of none.** cl. 96(4) would convert the position at §4.1 — no transfer restriction — into a conjunctive test. A hosting choice made now under Act 843 could require unwinding under the Bill. **This strengthens ADR-0009's deferral rather than weakening it**, and it is the clearest answer available to anyone who reads §4.1 and concludes the deferral was unnecessary.
2. **cl. 96(4)(a)'s consent condition is a live problem for an HRMS specifically**, and it is worth counsel's attention out of proportion to its length. It requires the *data subject's* "written, free, explicit and informed consent" to the transfer. The data subjects here are **employees**. Whether consent given by an employee to an employer is "free" is a contested question in data protection law generally, and the Bill does not appear to except employment. If employee consent cannot be relied on as free, cl. 96(4)(a) is not satisfiable for an HRMS by consent — and cl. 96(4) is conjunctive on its face ("the following conditions are met", (a) **and** (b) **and** (c)). Under Act 843 this problem does not arise, because Act 843 has no transfer condition at all; note that Act 843's own consent provision at s.20(1) offers alternatives to consent — including at s.20(1)(a) necessity "for the purpose of a contract to which the data subject is a party" and at s.20(1)(b) processing "authorised or required by law" — whereas cl. 96(4)(a) does not, on its face, offer an alternative to consent.
3. **HR data is largely outside the Bill's mandatory localisation list — but not certainly.** cl. 96(2) confines mandatory localisation to national-security data, national ID and civil registration systems, and "children's data, biometric data, health records and genetic data". Ordinary payroll and employee records are not listed. **Two caveats.** First, an HRMS may hold **health records** — sick leave, medical certificates, fitness-to-work records — and cl. 96(2)(c) would then bite on that subset; and cl. 97(1) would require Authority approval *and* the consent of all affected data subjects before processing special personal data out of Ghana. Second, cl. 96(2)(c) covers **biometric data**; this system does not hold any, because SRS §6.4 places biometric attendance integration and facial recognition attendance out of scope and TBD-013 is recorded as inert for this release (`docs/02-project-plan.md` §8.1). **That scope decision, taken for unrelated reasons, keeps the system outside one limb of the Bill's localisation list — and would stop doing so if TBD-013 were ever revisited.** That connection is recorded here because it is not recorded anywhere else, and because the cost of reopening TBD-013 would no longer be only an engineering cost.

## 5. Question 3 — Security, retention, breach

### 5.1 What the Act says: the eight principles

s.17 binds "a person who processes data" to eight principles: accountability, lawfulness of processing, specification of purpose, compatibility of further processing with purpose of collection, quality of information, openness, data security safeguards, and data subject participation. ss.18–26 elaborate them. The principles apply to this system's processing by force of s.45(1)(c) regardless of where it is hosted (§4.2(c)).

Provisions bearing directly on an HRMS:

- **s.19 (minimality)** — "Personal data may only be processed if the purpose for which it is to be processed, is necessary, relevant and not excessive."
- **s.20(1) (consent, justification)** — processing without prior consent is permitted where necessary for a contract to which the data subject is a party (a), authorised or required by law (b), to protect a legitimate interest of the data subject (c), necessary for the proper performance of a statutory duty (d), or necessary to pursue the legitimate interest of the controller or a third party (e). **Note s.20(2)–(3):** a data subject may object to processing "unless otherwise provided by law", and on objection "the person who processes the personal data **shall stop the processing**". The Act attaches no balancing test to s.20(3) on its face.
- **s.26 (quality)** — data must be "complete, accurate, up to date and not misleading".
- **s.27(2)** — nine items the data subject must be made aware of at collection, including the recipients of the data and the existence of the rights of access and rectification. This is a **notice** obligation distinct from the registration obligation at s.27(1), and it lives in the same section — which is a further reason the bare citation "s.27(1)" in ADR-0009 under-describes what s.27 contains.
- **ss.35, 41** — right of access; rights in relation to automated decision-taking.
- **s.43** — compensation for damage or distress through contravention.

### 5.2 What the Act says: security (s.28) — and its relation to HRMS-NFR-020

> **s.28(1)** "A data controller shall take the necessary steps to secure the integrity of personal data in the possession or control of a person through the adoption of **appropriate, reasonable, technical and organisational measures** to prevent (a) loss of, damage to, or unauthorised destruction; and (b) unlawful access to or unauthorised processing of personal data."

> **s.28(2)** "To give effect to subsection (1), the data controller shall take reasonable measures to (a) identify reasonably foreseeable internal and external risks…; (b) establish and maintain appropriate safeguards against the identified risks; (c) **regularly verify that the safeguards are effectively implemented**; and (d) ensure that the safeguards are **continually updated** in response to new risks or deficiencies."

> **s.28(3)** "A data controller shall observe (a) **generally accepted information security practices and procedure**, and (b) **specific industry or professional rules and regulations**."

**The standard is outcome-based and open-textured.** s.28 names no technology, no algorithm, no key length, and no protocol. It does not mention encryption, transport security, or HTTPS. **The Act therefore does not, on its own terms, mandate HRMS-NFR-020** (HTTPS in production) or any other specific control; what it does is make s.28(3)(a) — "generally accepted information security practices and procedure" — the route by which prevailing practice is incorporated by reference. Whether HRMS-NFR-020, HRMS-NFR-012, and the controls in `docs/07-iam-rbac.md` satisfy s.28 for this system is a judgement about what is "appropriate" and "reasonable" and about what is "generally accepted" — not a conformance check against a list, because the Act supplies no list.

Two obligations in s.28 are **ongoing** and have no counterpart in the SRS's non-functional requirements as written: s.28(2)(c) requires safeguards to be *regularly verified as effectively implemented*, and s.28(2)(d) requires them to be *continually updated*. Both are operating duties on a live controller rather than properties of a delivered system, and neither is a thing this project can discharge on the organisation's behalf.

**Processor obligations (ss.29–30)** are set out at §4.2(b). s.29 requires a processor to process only with the controller's prior knowledge or authorisation and to treat the data as confidential.

### 5.3 What the Act says: breach notification (s.31)

> **s.31(1)** "Where there are **reasonable grounds to believe** that the personal data of a data subject has been accessed or acquired by an unauthorised person, the data controller or a third party who processes data under the authority of the data controller shall notify the (a) Commission, and (b) the data subject of the unauthorised access or acquisition."

Key features, all on the face of the section:

- **The trigger is unauthorised access *or acquisition*, on reasonable grounds to believe.** There is no harm threshold and no risk threshold. There is no *de minimis*.
- **Both** the Commission **and** the data subject must be notified. s.31(1) is conjunctive.
- **Timing: "as soon as reasonably practicable after the discovery"** (s.31(2)). **The Act sets no fixed deadline** — no 72-hour rule, no fixed number of days. (The draft Bill is reported to introduce 72 hours; that is the Bill, not the law.)
- The controller "shall take steps to ensure the **restoration of the integrity of the information system**" (s.31(3)).
- Notification to the data subject is **delayed** only where security agencies or the Commission say it would impede a criminal investigation (s.31(4)).
- Permitted channels are enumerated at s.31(5): registered mail, electronic mail, prominent placement on the responsible party's website, publication in the media, or any other manner the Commission directs.
- The notification must contain "sufficient information to allow the data subject to take protective measures", including the identity of the unauthorised person if known (s.31(6)–(7)).
- The Commission may **direct publicity** where it believes publicity would protect affected data subjects (s.31(8)).

**Bearing on this system:** an s.31 obligation is an *operational* obligation on a live controller, and it presupposes that a breach can be **discovered** — which presupposes detection and logging. The audit-log design at `docs/07-iam-rbac.md` §7.3 and the off-host audit sink recorded there against TBD-003 are the closest thing this project has to a mechanism serving s.31(1)'s "reasonable grounds to believe". This brief does not assert that they satisfy it.

### 5.4 What the Act says: retention (s.24) — bearing on TBD-009

**This is the part of the Act that bears on TBD-009, and it does not close it.**

> **s.24(1)** "Subject to subsections (2) and (3), a data controller who records personal data **shall not retain the personal data for a period longer than is necessary to achieve the purpose for which the data was collected and processed** unless (a) the retention of the record is **required or authorised by law**, (b) the retention of the record is reasonably necessary for a lawful purpose related to a function or activity, (c) retention of the record is required by virtue of a **contract** between the parties to the contract, or (d) the **data subject consents** to the retention of the record."

> **s.24(4)** "A person who **uses a record of the personal data of a data subject to make a decision about the data subject** shall (a) retain the record for a period **required or prescribed by law or a code of conduct**, or (b) where there is no law or code of conduct that provides for the retention period, retain the record for a period which will **afford the data subject an opportunity to request access to the record**."

> **s.24(5)** "A data controller shall **destroy or delete** a record of personal data **or de-identify** the record at the expiry of the retention period."

> **s.24(6)** "The destruction or deletion of a record of personal data shall be done in a manner that **prevents its reconstruction in an intelligible form**."

s.24(2)–(3) except records retained for historical, statistical, or research purposes, subject to adequate protection against unauthorised access or use.

**What this means for TBD-009, precisely.**

1. **The Act sets no retention period.** Not for employee records, not for payroll records, not for anything. **s.24 is a *rule for deriving* a retention period, not a period.** It says: retain no longer than necessary for the purpose, unless one of four exceptions applies. TBD-009 asks what the document retention policy is; **s.24 tells you how to answer that question and does not answer it.** The answer depends on the purposes the organisation actually pursues and on the other laws that bind it — neither of which exists while TBD-001 is open. **TBD-009 is therefore correctly recorded in `docs/02-project-plan.md` §8.1 as "Open. Not resolvable by this project", and reading Act 843 does not change that.** If anything it explains *why* it is not resolvable: the statute delegates the period to facts this project does not have.
2. **s.24(1)(a) is the hook that makes payroll retention someone else's question.** Payroll records supporting PAYE and SSNIT contributions are very likely retained under "required or authorised by law" — but *which* law, and for how long, is revenue and pensions law, **not Act 843**. Act 843 defers to those instruments and does not name them. This brief did not survey them (§4.4).
3. **s.24(4) reaches this system directly, and reaches further than it first appears.** An HRMS exists to make decisions about data subjects — payroll runs, leave approvals, compensation changes, employment status changes. Records used for those decisions attract s.24(4). Where no law or code prescribes a period, the floor is a period that affords the data subject an opportunity to request access. **The Act does not say how long that is.** It is a standard, not a number, and it is left to judgement.
4. **s.24(5)–(6) are requirements on the system, not only on the policy, and they are the operative point for this project.** Whatever period TBD-009 eventually sets, the system must be able to **destroy, delete, or de-identify** at its expiry, in a manner **preventing reconstruction in an intelligible form**. That is a design constraint that **does not depend on knowing the period**, and it therefore does not depend on TBD-009 closing. It bears on:
   - **`docs/adr/0007-s3-compatible-storage-for-employee-documents.md`** and M4 document storage — object deletion, versioning, and whether a deleted object is reconstructible;
   - **HRMS-DR-010** and `CONTEXT.md`, which require compensation changes to be stored as history and **never overwritten** — history that is never overwritten still reaches an expiry under s.24(1) and must then be destroyed or de-identified under s.24(5). **Immutability and s.24(5) are in tension and the Act does not resolve it**; de-identification under s.24(5) is the obvious candidate but whether it suffices is a judgement;
   - **`docs/07-iam-rbac.md` §7.3**, where audit records are held under a PostgreSQL grant of `INSERT` and `SELECT` only, with **no `DELETE`**. If audit records contain personal data and reach a retention expiry, **s.24(5) requires a deletion or de-identification capability that the current grant does not provide to any party below the operational ceiling that record describes.** This is the sharpest interaction found between the Act and an existing design decision. It is **not** an assertion that the design is unlawful — it is an observation that a requirement to destroy and a grant that cannot delete are pulling in opposite directions, and that nobody has yet asked which wins.
   - **HRMS-NFR-012** (backups). A backup contains personal data. s.24(5) requires destruction at expiry of the retention period; whether and how that reaches backup copies is not addressed by the Act.
5. **`docs/01-srs.md` §1 records "Organization Data Protection Policy | TBD"** as a reference document. s.24 is one reason that document has to exist before the retention question can be closed.

### 5.5 What the Act says: special personal data (s.37) — and payroll

**Payroll data is not special personal data.** s.37(1) confines the category to data relating to a child under parental control, or to "the religious or philosophical beliefs, ethnic origin, race, trade union membership, political opinions, health, sexual life or criminal behavior of an individual". **Salary, PAYE, and SSNIT contribution records are not in that list**, and are ordinary personal data.

An HRMS may nonetheless hold special personal data incidentally — **health** (sick leave, medical certificates), **trade union membership** (where deductions are administered), **criminal behaviour** (where background checks are held), **ethnic origin** or **religious belief** (where recorded at all). Whether this system holds any is a design question that has not been asked in these terms, and s.47(1)(d) makes it a **registration particular**: the application must indicate "whether the applicant holds or is likely to hold special personal data".

The employer gateway is s.37(3):

> **s.37(3)** "The processing of special personal data **is necessary** where it is for the exercise or performance of a **right or an obligation conferred or imposed by law on an employer**."

which, read with s.37(2)(a) — a controller may process special personal data where "processing is necessary" — is the provision an employer would rely on.

**An ambiguity, stated not filled:** the Act **does not define "special personal data" in s.96**, its interpretation section, although it uses the term as a term of art in ss.37–38 and s.47(1)(d). The category is knowable only by inference from the enumeration in s.37(1). Whether that enumeration is exhaustive for s.47(1)(d)'s purposes is not settled by the text.

### 5.6 What requires legal judgement

- Whether the measures in `docs/07-iam-rbac.md`, HRMS-NFR-012, and HRMS-NFR-020 are "appropriate, reasonable, technical and organisational" for **this** controller's risk under s.28(1), and what "generally accepted information security practices" (s.28(3)(a)) means for an HRMS in Ghana.
- Whether any "specific industry or professional rules and regulations" (s.28(3)(b)) attach to payroll or HR data.
- What retention period s.24 yields for each record class — which requires the organisation's purposes and a survey of the other laws s.24(1)(a) defers to.
- **How s.24(5) is reconciled with HRMS-DR-010's never-overwritten compensation history and with the append-only audit grant at `docs/07-iam-rbac.md` §7.3** (§5.4(4)).
- Whether the system holds special personal data within s.37(1), and whether s.37(3) covers each instance.
- Whether s.20(3) — stop processing on objection — has any application to an employee objecting to payroll processing, and how it interacts with s.20(1)(b) and (d).
- Whether an s.57 Executive Instrument makes any HRMS processing assessable (§3.5).

## 6. Question 4 — Timing: does anything attach before an operating organisation exists?

### 6.1 What the Act says

**The Act answers this squarely, and the answer is no — with a short fuse once business begins.**

> **s.97(1)** "A data controller **incorporated or established after the commencement of this Act** shall be required to register as a data controller **within twenty days of the commencement of business**."

> **s.97(2)** "A data controller **in existence at the commencement of this Act** shall be required to register as a data controller within three months after the commencement of this Act."

s.97(1) is the applicable limb: any organisation that comes into existence for this HRMS would be incorporated or established long after Act 843's commencement. **The obligation is keyed to two events, and neither has occurred:**

1. **Being incorporated or established** — TBD-001 records that no organisation exists.
2. **Commencement of business** — which cannot precede (1).

The trigger at s.27(1) is likewise a **data controller** who "intends to process personal data". s.96 defines a data controller as a **person**. **There is no controller.** There is no person who determines the purposes and manner of processing anyone's personal data, because there is no organisation and there is no personal data.

The offence at s.56 requires that a person "**fails to register as a data controller but processes personal data**". Both limbs must be satisfied. **Neither is.** `docs/02-project-plan.md` §8.3 records that "No production personal data of any Ghanaian employee is placed in any environment while TBD-003 is open. There is none to place, and this is recorded so that convenience does not later supply some."

**On the facts recorded in the TBD register — no organisation, no controller, no live data — no obligation under Act 843 has attached to anything this project has done or plans to do.** Development against synthetic or fabricated data, by a person who is not a controller, for an organisation that does not exist, does not engage s.27(1), s.53, or s.56 on the face of those sections.

**ADR-0009's framing is confirmed.** That record states: "There is no controller to register, no counsel to advise, and no production personal data. Selecting a hosting provider today would be precision without basis." **s.97(1) is the statutory basis for that sentence**, and ADR-0009 arrives at the right position without having cited it. This brief supplies the citation.

### 6.2 The part that matters for planning: twenty days

**s.97(1) gives twenty days from commencement of business.** That is a short window, and it has three consequences worth recording, none of which is a legal conclusion:

1. **Registration is not a step that can be scheduled comfortably after go-live.** s.53 prohibits an unregistered controller from processing personal data at all. Read with s.97(1), an organisation that begins business and begins processing employee data has twenty days — and s.53 arguably bites from the first day of processing rather than the twenty-first, since s.97(1) sets a *registration deadline* while s.53 sets a *prohibition on processing*. **Whether s.97(1) grants a twenty-day grace period during which s.53 does not bite, or whether s.53 bites immediately and s.97(1) merely fixes the outer limit for the registration itself, is a question of construction the Act does not resolve on its face.** The two readings differ materially for any go-live plan, and this brief does not choose between them.
2. **s.47(1)(g) means the hosting question must be answered *at registration*, not after it.** The application must state the country to which the controller may transfer data. Since registration falls due within twenty days of commencement of business, **the destination country is needed at roughly the same moment the organisation starts operating** — which is to say, TBD-003 and TBD-001 come due together rather than in sequence. `docs/02-project-plan.md` §8.1 records TBD-003's resolution point as "See §8.3" and TBD-001's as "Before Stage 9. Not before". **s.47(1)(g) is a reason those two cannot be sequenced far apart**, and this is the one genuinely new scheduling fact in this brief. It does not change that neither is resolvable now.
3. **If s.57 assessable processing applies, add 28 days** before processing may begin (s.57(5)), which would sit awkwardly inside a twenty-day registration window. Whether it applies is at §3.5.

### 6.3 What requires legal judgement

- Whether anything done in development — synthetic data, a demonstration deployment, the author's own details used as test data — could constitute processing personal data by a controller. **Note the author's own personal data is capable of being personal data**; whether a solo developer processing their own details for testing is a "data controller" processing "personal data" within the Act is not a question this brief answers.
- When "commencement of business" occurs for s.97(1) — a question that may not have an obvious answer for a new entity, and one that starts a twenty-day clock.
- Whether s.53's prohibition and s.97(1)'s twenty-day deadline are consistent, and which governs in the first twenty days (§6.2(1)).
- Whether registration can or should be applied for **before** commencement of business, given that s.27(1)'s trigger is an *intention* to process — which appears to permit earlier registration but is not stated to require it.
- Whether the eventual organisation is the controller, or whether some other person is.

## 7. Bearing on ADR-0009 and the TBD register

**No TBD is closed by this brief, and none could be.** TBD-003 requires counsel and an organisation; this document is neither. What follows is what the brief bears on, stated so that a reader of ADR-0009 can see what has and has not moved.

### 7.1 Where the reading supports ADR-0009

| ADR-0009 states | This brief finds |
|---|---|
| Act 843 sets out no adequacy regime of the GDPR kind; the earlier "adequate level of protection" claim is withdrawn as unsupported | **Supported, and more strongly than the record claims.** Read in full, the Act contains no transfer restriction at all — not an adequacy test with a missing list, but no test. The withdrawal was correct (§4.1) |
| The position is "open, not permissive" | **Supported.** The absence of a prohibition is not a permission: s.48(1)(b), s.30(4), and unsurveyed sector law all stand in the way (§4.4) |
| Registration is required, and the particulars include destination countries | **Supported** — s.27(1), s.46(3), s.47(1)(g) (§3.1, §3.2) |
| Penalties are in penalty units, not a monetary ceiling or a turnover proportion | **Supported** — ss.47(2), 56, 57(6), 80(1), 95 (§3.4) |
| The Bill 2025 is "reported" to propose localisation, TIAs, and approval for high-risk transfers | **Supported, and upgraded from report to draft text** — cll. 96(1), 96(4)(c), 97(4). Still a draft, still not introduced (§4.5) |
| There is no controller to register and no production personal data, so the question cannot be answered now | **Supported, with a citation the record lacks** — s.97(1) keys the obligation to commencement of business (§6.1) |

### 7.2 Where the reading adds something ADR-0009 does not have

1. **s.30(4) is the provision the decision rule should be pointed at, and it is not mentioned anywhere in this repository.** ADR-0009's condition 1 asks counsel "whether the Act restricts transfer of that data outside Ghana, on what test, and what a lawful transfer requires". The Act's answer to "on what test" is: **there is no transfer test — there is a processor-compliance obligation instead.** s.30(4) requires the controller to *ensure* a non-domiciled processor complies with Ghanaian law, under a written contract meeting s.30(2)–(3). **That is the provision most likely to constrain a hosting choice in practice**, and a question to counsel framed only around "transfer restrictions" may miss it, because counsel would correctly answer that there are none. §8 reframes the question accordingly.
2. **s.47(1)(g) couples TBD-003 to TBD-001 more tightly than §8.1 records** (§6.2(2)): the destination country is a registration particular, and registration falls due within twenty days of commencement of business.
3. **s.24(5)–(6) is a design constraint that does not wait for TBD-009** (§5.4(4)): the ability to destroy or de-identify irreversibly is required whatever the period turns out to be. It interacts with ADR-0007, HRMS-DR-010, HRMS-NFR-012, and — most sharply — with the append-only audit grant at `docs/07-iam-rbac.md` §7.3, which holds `INSERT` and `SELECT` only and therefore cannot delete.
4. **s.28 does not mandate HRMS-NFR-020 or any specific control** (§5.2). The Act's standard is "appropriate, reasonable" measures plus "generally accepted information security practices". ADR-0009's condition 3 treats HRMS-NFR-020, HRMS-NFR-012, and HRMS-NFR-035 as things a hosting target must satisfy, which is right as a *project* requirement — but this brief records that **their statutory necessity is not established by Act 843**, and that s.28(2)(c)–(d) impose *ongoing* verification and update duties that no delivered system discharges.
5. **The registration citation in ADR-0009 and `docs/02-project-plan.md` §8.3 is incomplete** (§3.1): s.27(1) creates the duty; ss.46–56 and s.97 carry the machinery and the deadline.

### 7.3 What contradicts nothing

**No finding in this brief contradicts ADR-0009, `docs/02-project-plan.md`, or any other record in this repository.** This is worth stating explicitly, because ADR-0009 has twice had to withdraw a legal claim, and a research brief arriving after those withdrawals could be expected to find a third. It does not. The record's current position — that the Act plainly imposes registration and destination disclosure, that a transfer restriction of any particular shape is an interpretation for counsel, and that the deferral stands on the absence of a controller rather than on the size of a penalty — **is what the statute supports.**

The one qualification is at §7.2(4): ADR-0009 does not claim Act 843 mandates HRMS-NFR-020, so there is no contradiction; but a reader could take condition 3's placement alongside condition 1 to imply a statutory source for those NFRs, and there is none in Act 843.

## 8. Questions for counsel

Scoped so that each can be answered without re-reading the Act, and ordered by what ADR-0009's decision rule needs. **These replace nothing in the decision rule; they are an attempt to make its condition 1 cheaper to satisfy.**

**On hosting — ADR-0009 condition 1**

1. We read Act 843 as containing **no restriction on transferring or hosting personal data outside Ghana** — the only operative reference to transfer being the registration particular at s.47(1)(g), and s.18(2) applying only to foreign data subjects whose data is sent *into* Ghana. **Is that reading right?**
2. If it is: what work is **s.30(4)** doing? Can a controller "ensure" that a non-domiciled cloud provider "complies with the relevant laws of this country" on that provider's standard terms — and what does a s.30(2) written contract have to contain to satisfy ss.30(3) and 30(4)?
3. How does the Commission treat **offshore hosting at registration in practice**, under its s.48(1)(b) power to refuse where "appropriate safeguards… have not been provided"? Is there a destination it would refuse, and is that discretion exercised in a way that functions as a transfer rule despite the Act containing none?
4. **Does any law outside Act 843 restrict where payroll, PAYE, SSNIT, or employment records may be held** — revenue, pensions, companies, or banking law? We did not survey these, and our finding on Act 843 says nothing about them.
5. If the **Data Protection Bill, 2025** is enacted substantially as drafted, would a hosting arrangement lawful under Act 843 need to change? Specifically: **can cl. 96(4)(a)'s requirement of "written, free, explicit and informed consent" ever be satisfied by an *employee*** — and if not, is cl. 96(4) satisfiable at all for an HRMS, given it reads conjunctively?

**On registration**

6. Would the organisation be a **data controller**, a data processor, or both? Does any exemption in ss.60–74 touch an HRMS?
7. Which **L.I. 2512 band** applies, given that the Small and Medium criteria overlap (§3.3)? Is renewal under s.50 charged at the registration fee, and is L.I. 2512 the instrument s.59 contemplates?
8. Does processing an HRMS's data constitute **assessable processing** under s.57 — i.e. is there an Executive Instrument in force, and would the 28-day bar at s.57(5) apply?
9. **Is contravening s.53 a distinct offence under the s.95 general penalty (5,000 penalty units / 10 years), or is s.56 (250 penalty units / 2 years) the exhaustive sanction for processing while unregistered?** (§3.5.)

**On timing — the twenty-day window**

10. We read **s.97(1)** as meaning no registration obligation attaches until the organisation exists and commences business, and then within twenty days. **Is that right, and when does "commencement of business" occur** for a newly established entity?
11. **Does s.53 prohibit processing during those twenty days**, or does s.97(1) afford a grace period? The two readings differ materially for any go-live plan (§6.2(1)).
12. Can — or should — registration be applied for **before** commencement of business, given s.27(1) is triggered by an *intention* to process? Since s.47(1)(g) requires the destination country at application, this determines how early TBD-003 must close.
13. Does anything we do **in development** — synthetic data, a demonstration deployment, the author's own details as test data — engage the Act?

**On retention and security**

14. What retention period does **s.24** yield for employee records, payroll records supporting PAYE and SSNIT, and HR documents — and which other laws does s.24(1)(a) defer to here? This is the substance of **TBD-009**.
15. **How is s.24(5) — destroy, delete, or de-identify at expiry, irreversibly under s.24(6) — reconciled with (a) HRMS-DR-010's requirement that compensation history is never overwritten, and (b) an audit log we hold append-only, with `INSERT`/`SELECT` and no `DELETE`?** Is de-identification sufficient for both?
16. Does **s.24(5)** reach backup copies (HRMS-NFR-012), and if so how?
17. Does an HRMS hold **special personal data** within s.37(1) — health records from sick leave, trade union membership from deductions, criminal behaviour from background checks — and does **s.37(3)** cover each? This is a **registration particular** under s.47(1)(d).
18. What do "**generally accepted information security practices and procedure**" (s.28(3)(a)) mean for an HRMS in Ghana, and do any "specific industry or professional rules" (s.28(3)(b)) attach to payroll data?
19. Does **s.20(3)** — stop processing on the data subject's objection — have any application to an employee objecting to payroll processing, given s.20(1)(b) and (d)?

## 9. Standing caveat

**Nothing in this document is legal advice.** It is a reading of a statute by a person not qualified to interpret it, assembled to make a question to counsel shorter. Every finding in §§3–6 labelled "what the Act says" is a quotation or a direct paraphrase with a citation, and may still be wrong in its selection, its emphasis, or its relevance. Every judgement about applying those provisions has been left where it belongs.

**This brief resolves no TBD.** TBD-003 is open. TBD-001 is open. TBD-009 is open. `docs/02-project-plan.md` §8.2 records all three among the eleven not resolvable by this project, and this document does not move any of them. ADR-0009's decision rule is unchanged and unsatisfied: condition 1 requires **written confirmation from qualified legal counsel**, and a document the project wrote about itself is not that, however many sections it cites.

**On the temptation this document creates.** The finding at §4.1 — that Act 843 contains no restriction on hosting outside Ghana — is the kind of finding that invites a reader to conclude the hosting question is easier than ADR-0009 made it, and to reach for a provider. **It does not support that conclusion.** ADR-0009 defers the hosting target because there is no controller, no counsel, and no data — **not** because a transfer restriction was believed to exist. Removing a restriction that was never established does not remove a deferral that never rested on it. The three obstacles at §4.4 — the Commission's s.48(1)(b) discretion, the obligation of result at s.30(4), and sector law this brief did not survey — remain, and the draft Bill at §4.5 points toward more restriction rather than less.

**Following the ADR's standing instruction.** ADR-0009 records that it "states only the obligations the Act plainly imposes, marks everything else as an open question for counsel, and does not replace a withdrawn assertion with a better-sounding one. Where the honest position is that the position is unknown, that is what is written." This brief is written to the same instruction. Two claims are marked **[UNVERIFIED]** at §2 and are not repaired by inference: the cedi value of a penalty unit, and Act 843's commencement date. Several ambiguities are recorded as ambiguities — the s.53/s.95 overlap (§3.5), the L.I. 2512 band criteria (§3.3), the missing definition of "special personal data" (§5.5), the s.53/s.97(1) tension (§6.2) — rather than resolved by picking the reading that reads best. **Where the Act is silent, this brief says the Act is silent.**
