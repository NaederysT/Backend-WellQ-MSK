# WellQ — MongoDB Collection Reference

> Conversión a Markdown del documento PDF **WellQ db collection model.docx.pdf**.

## Metadatos del documento

- **Backend:** `dev_wq`
- **Última actualización:** 2026-04-18
- **Fuente de verdad indicada:** `app/models/`, `app/db.py`, `app/api/v1/routers/`
- **Leyenda:** 🔑 = campo indexado; 🔗 = referencia tipo foreign-key hacia otra colección.

## Índice de colecciones

| Grupo | Colecciones |
|---|---|
| 🔐 Auth & Identity | `usuarios, invitations, push_tokens` |
| 🏥 Organisation | `clinics, clinicians, specialities_catalog` |
| 🧑‍⚕️ Patient Core | `patients, cases, intakes, consents, historial_medico` |
| 📊 Check-ins & Metrics | `checkins, metrics` |
| 🗺️ Body Charts | `map_structinteg` |
| 📅 Appointments & Notes | `appointments, clinical_notes` |
| 🏋️ Exercise System | `ejercicios_catalogo, program_templates, patient_programs, clinical_programs, scheduled_exercises, patient_routines, patient_workout_logs, patient_custom_exercises` |
| 🎯 Patient Goals & Engagement | `patient_goals, patient_commitments` |
| 🔔 Alerts & Communications | `alerts, communications_log, actions_log` |
| 📋 Diagnostics | `diagnostic_codes, diagnoses_sections` |
| ⚙️ Admin & Config | `state_rule_configs, credentials, legal_docs` |
| 🎟️ Support Tickets | `ticket, ticket_categories, channels, email_template, email_config, email_infoticket, responder` |
| 🖼️ Media | `media` |

## Referencia detallada

> Nota: Las tablas originales del PDF se preservan como bloques `text` para mantener alineación de columnas, campos, tipos, obligatoriedad y relaciones.


### Página 2

```text
🔐 Auth & Identity
usuarios

Auth user accounts. This is the primary authentication collection.

                                     Re
 Field                  Type                Description                                 Relations
                                     q

 _id                    ObjectId     ✅ MongoDB document ID                              —

 email                  string       ✅ Login email address (normalised)                 —

 hashed_password        string       ✅ bcrypt hashed password                           —


 roles                  string[]     ✅ Permission
                                       roles: patient, clinician, admin
                                                                                        —
```

### Página 3

```text
Re
 Field                    Type                   Description                               Relations
                                         q

 patient_id               string         —       🔗 Links to patients.patient_id            → patients


 clinician_id             string         —       🔗 Internal clinician identifier           → clinician
                                                                                           s

                                                 JWT ID for the current active refresh
 jti                      string         —                                                 —
                                                 session

 refresh_token            string         —       Opaque refresh token (hashed or raw)      —

 refresh_expires_a
                          datetime       —       Expiry timestamp of the refresh session   —
 t

 is_active                bool           —       Whether the account is enabled            —

 created_at               datetime       —       Account creation timestamp                —

 updated_at               datetime       —       Last account update timestamp             —

Key indexes: email (unique), jti



invitations

One-time invitation tokens for clinician onboarding.

                                                                                            Relation
 Field           Type              Req        Description
                                                                                            s

 _id             ObjectId          ✅ MongoDB document ID                                    —


 token_hash      string            ✅ 🔑 SHA-256
                                       (unique)
                                                hash of the invitation token
                                                                                            —


 email_nor
 m
                 string   ✅ 🔑 Normalised invitation target email                            —


 expires_at      datetime ✅ 🔑 Token expiry timestamp                                        —

 used            bool              —          Whether the invitation has been claimed       —

 clinic_id       string            —          🔗 Clinic the invitee will belong to           → clinics
```

### Página 4

```text
Relation
 Field            Type          Req        Description
                                                                                            s

 roles            string[]      —          Roles to assign on acceptance                    —

 created_at       datetime      —          Invitation issue timestamp                       —

Key indexes: token_hash (unique), email_norm, expires_at, compound (used, expires_at)



push_tokens

Mobile FCM push notification tokens, one per user-device pair.

 Field            Type         Req         Description                                    Relations

 _id              ObjectId     ✅ MongoDB document ID                           —


 user_id          string       ✅ 🔑 🔗 Patient patient_id (used for FCM lookup) →s patient
 fcm_token        string       ✅ 🔑 Firebase Cloud Messaging device token —
 is_active        bool         —           Whether this token is still valid              —

 platform         string       —           ios or android                                 —

 created_at       datetime     —           Token registration timestamp                   —

 updated_at       datetime     —           Last update (token rotation, revocation)       —

Key indexes: compound (user_id, fcm_token) (unique), user_id, is_active, updated_at



🏥 Organisation
clinics

Physical or virtual clinic/practice locations.

                                                                                      Relation
 Field            Type         Req         Description
                                                                                      s

 _id              ObjectId     ✅ MongoDB document ID                                  —

 name             string       ✅ 🔑 Display name of the clinic                         —

 address          string       —           Physical street address                    —
```

### Página 5

```text
Relation
 Field            Type         Req         Description
                                                                                         s

 phone            string       —           Contact phone number                          —

 email            string       —           Contact email address                         —

 state            string       —           Lifecycle state: active, inactive, disabled   —

 metadata         dict         —           Arbitrary key-value extension fields          —

 created_at       datetime     —           Creation timestamp                            —

 updated_at       datetime     —           Last update timestamp                         —

Referenced
by: clinicians.clinic_id, clinicians.clinic_ids[], patients.clinic_ids[], program_templates.clinic_id, appoi
ntments.clinic_id, state_rule_configs.clinic_id



clinicians

Clinical staff profiles. ids.tm3 is the key field for TM3 sync.

                                 Re                                                          Relation
 Field            Type                   Description
                                 q                                                           s

 _id              ObjectId       ✅ MongoDB document ID                                       —

 first_name       string         —       Given name                                          —

 last_name        string         —       Family name                                         —

                                         External system identifiers: norm_id, tm3,
 ids              dict           —                                                           —
                                         etc.

 contact          dict           —       { email, phone } contact info                       —

 specialties      string[]       —       List of clinical specialties                        —

 clinic_id        ObjectId       —       🔗 Primary/default clinic                            → clinics

 clinic_ids       ObjectId[]     —       🔗 All associated clinics (n-to-m)                   → clinics

 state            string         —       active or inactive                                  —
```

### Página 6

```text
Re                                                     Relation
 Field              Type                     Description
                                      q                                                      s

 metadata           dict              —      Arbitrary extension fields                      —

 created_at         datetime          —      Creation timestamp                              —

 updated_at         datetime          —      Last update timestamp                           —

Key indexes: clinician_id (unique), contact.email, (last_name, first_name), clinic_id, clinic_ids
Referenced
by: patients.care_clinician_id, patients.authorized_clinicians[], cases.primary_provider_id, appointm
ents.provider_id, program_templates.clinician_id, clinical_programs.clinician_id



specialities_catalog

Lookup table of clinical specialties.

                           Re
 Field     Type                       Description
                           q

 _id       ObjectId        ✅ MongoDB document ID
 name      string          ✅ Specialty display name
 code      string          —          Short code identifier



🧑‍⚕️ Patient Core
patients

Core patient entity. Root of all patient-related data.

                                                Re
 Field                         Type                   Description                        Relations
                                                q

 _id                           ObjectId         ✅ MongoDB document ID                    —

                                                      Root-level primary key,
 patient_id                    string
                                                🔑
                                                —
                                                      e.g. P-RM6P3HWSRGWC (elevate
                                                      d from ids in Apr 2026)
                                                                                         —



 first_name                    string           —     Given name (aliases: nombres)      —

 last_name                     string           —     Family name (aliases: apellidos)   —
```

### Página 7

```text
Re
Field                  Type              Description                             Relations
                                    q

                                         Date of birth
dob                    datetime     —                                            —
                                         (aliases: fecha_nacimiento)

gender                 string       —    Gender (aliases: sexo)                  —

contact                dict         —    { phone, email }                        —

                                         Structured address
address                dict         —                                            —
                                         (aliases: direccion)

                                         External system
ids                    dict         —                                            —
                                         map: cliniko, nookal, tm3, etc.

                       MedicalAle        Embedded clinical flags (type,
medical_alerts                      —                                            —
                       rt[]              message)

                       ReferralSo        Origin of referral: type, name,
referral_source                     —                                            —
                       urce              contact_id

care_clinician_id      ObjectId     — 🔗 Primary assigned clinician → clinicians
authorized_clinicia
ns
                       ObjectId[]   — 🔗 Secondary viewer clinicians → clinicians
clinic_ids             ObjectId[]   —
                                      🔗 Clinics this patient is assigned → clinics
                                         to

                                         Static height in cm (set at
height                 float        —                                            —
                                         onboarding or via admin)

                                         active or inactive (aliases: estado
state                  string       —                                            —
                                         )

                                         Clinical
status                 string       —    status: stable, declining, at_risk, i   —
                                         mproving

active_rule_config_
                       string       —
                                         🔗 Override StateRuleConfig for          → state_rule_c
id                                       this patient                            onfigs

notifications_prefer                     FCM/SMS notification timing
                       dict         —                                            —
ences                                    preferences
```

### Página 8

```text
Re
 Field                   Type                 Description                           Relations
                                        q

 metadata                dict           —     Arbitrary extension fields            —

 created_at              datetime       —     Registration timestamp                —

 updated_at              datetime       —     Last update timestamp                 —

Key indexes: patient_id (unique, sparse), ids.patient_id, last_name, contact.phone,
compound (care_clinician_id, state)
Referenced
by: cases.patient_id, checkins.user_id, map_structinteg.user_id, appointments.patient_id, alerts.pati
ent_id, consents.patient_id, intakes.patient_id, historial_medico.paciente_id, patient_goals.patient_i
d, patient_commitments.patient_id, patient_programs.patient_id, credentials.patient_id, communic
ations_log.patient_id, push_tokens.user_id



cases

Episode of Care. Auto-created on onboarding. Central aggregation point for a treatment episode.

                                      Re
 Field                   Type                Description                        Relations
                                      q

 _id                     ObjectId     ✅ MongoDB document ID                     —


 patient_id              ObjectId
                                      ✅
                                      🔑 🔗 Reference to the patient              → patients


 status                  string
                                  ✅
                                  🔑 d
                                    active, closed, pending, on_hol
                                                                    —



 title                   string   ✅ Description,
                                    Pain – 2024"
                                                 e.g. "Lower Back
                                                                    —


 start_date              datetime ✅ Episode start date              —

 end_date                datetime     —      Episode close date                 —

                                             Date of injury
 injury_date             datetime     —                                         —
                                             (TM3/compensable cases)

 primary_provider_i
                         ObjectId     —
                                             🔗 Lead clinician (may be           → clinicians
 d                                           unset at creation)
```

### Página 9

```text
Re
 Field                    Type               Description                       Relations
                                      q


 care_team_ids
                          ObjectId[
                          ]
                                      —      🔗 All contributing clinicians     → clinicians


                                                                               → diagnostic_code
 diagnosis_codes          string[]    —      ICD-10 or internal codes
                                                                               s

 referral_id              ObjectId    —      🔗 Associated referral             —

 treatment_goals          string[]    —      Plain-text treatment objectives   —

 discharge_summar
                          string      —      Free-text discharge notes         —
 y

                                             { all_zones_ever_affected[],
                                             total_sessions,
                                             patient_sessions,
 overall_summary          dict        —      clinician_sessions,               —
                                             latest_assessment_date,
                                             latest_assessment_by,
                                             onboarding_baseline{} }

Key indexes: patient_id, status
Referenced by: appointments.case_id, clinical_notes.case, map_structinteg.case_id



intakes

Raw onboarding and questionnaire payloads. Flexible blob store.

 Field         Type          Req      Description                                      Relations

 _id           ObjectId      ✅        MongoDB document ID                              —


                             🔑 🔗 Patient identifier
                             —                                                         → patient
 patient_id    string
                                                                                       s


 type          string
                             ✅
                             🔑 Intake type, e.g. onboarding_patient                    —


                                      Flexible JSON payload (questionnaire answers,
 data          dict          —                                                         —
                                      pain map, goals, etc.)


                             🔑
 created_a                   —
               datetime               Submission timestamp                             —
 t
```

### Página 10

```text
Key indexes: patient_id, type, created_at



consents

Patient legal consent documents with full lifecycle tracking.

 Field             Type        Req        Description                            Relations

 _id               ObjectId ✅ MongoDB document ID                —


 patient_id        string   ✅ 🔑 🔗 Patient identifier             → patient
                                                                 s

 type              string   ✅ Document type: tcon, privacy, etc. —
 version           string   ✅ Version of the document, e.g. v2 —
 state             string   ✅ 🔑 valid or withdrawn               —

 signed_at         datetime ✅   When the consent was signed      —

 revoked_at        datetime    —          When consent was revoked               —

 observation
                   string      —          Free-text notes                        —
 s

 created_at        datetime    —          Record creation timestamp              —

 updated_at        datetime    —          Last update timestamp                  —

Key indexes: compound (patient_id, state)



historial_medico

Derived clinical status history. One document per patient. Written by the reclassification job (runs
every 8h).

 Field              Type        Req      Description                            Relations

 _id                ObjectId    ✅ MongoDB document ID                           —

                                ✅ 🔗 Patient identifier (unique per
 paciente_id        string
                                🔑        patient)
                                                                                → patients
```

### Página 11

```text
Field                  Type           Req       Description                             Relations

                                                 Current status: { est_act_nom,
 estado_act             dict           —                                                 —
                                                 est_act_ini }

                                                 Status history: { est_hist_nom,
 estado_hist            dict[]         —                                                 —
                                                 est_hist_ini, est_hist_fin }[]

                                                 Active exercises (legacy;               → ejercicios_catalog
 ejercicio_act          dict[]         —
                                                 superseded by patient_programs)         o

 sport_lifestyl                                  Hobby sport sessions with
                        dict[]         —                                                 —
 e                                               timestamps and metrics

 created_at             datetime       —         First classification timestamp          —

Key indexes: paciente_id (unique), created_at, compound status indexes
Note: Status values used for dashboard alert severity: at_risk → red, declining → orange.



📊 Check-ins & Metrics
checkins

Daily/weekly patient self-report check-ins. Also used for Day-0 baseline seeding on onboarding.

                                   R
 Field            Type             e         Description                          Relations
                                   q

 _id              ObjectId         ✅ MongoDB document ID                          —

 check_in_i
 d
                  string           ✅ Client-generated
                                     check-in ID
                                                      unique
                                                                                  —


                                   ✅ 🔗 Patient identifier
 user_id          string
                                   🔑 (patient_id)                                 → patients


 timestamp        datetime
                                   ✅
                                   🔑 Check-in date/time                           —


 type             string           ✅ daily, weekly, monthly, weight
                                     , onboarding_seed
                                                                    —


 mood             int              ✅ Mood rating 0–2                —

 pain_level       int              —         Pain rating 0–10                     —
```

### Página 12

```text
R
 Field           Type          e    Description                        Relations
                               q

 stiffness_l
                 int           —    Stiffness rating 0–10              —
 evel

                                    { value: float, unit: "kg"|"lbs"
 weight          dict          —                                       —
                                    }

 sleep_sess      SleepSessi         [{ session_id, start_time,
                               —                                       —
 ions            on[]               end_time, source }]

                                    [{ session_id, exercise_type,
 exercise_s      ExerciseSe                                            → ejercicios_catalogo (exerci
                               —    sets, reps, duration_seconds,
 essions         ssion[]                                               se_type = eje_cod)
                                    timestamp }]

                 PSFSItem[
 psfs                          —    [{ task, area, score 0–10 }]       —
                 ]

 health_me                          { bone, muscle, joint, cardio
                 dict          —                                       —
 trics                              } pillar scores (0–100)

 notes           string        —    Free-text patient note             —

 metadata        dict          —    Extension fields                   —

Key indexes: user_id, timestamp
Note: Each pillar in health_metrics is resolved independently from the most recent non-zero check-in
(fixed Apr 2026).



metrics

Raw wearable/sensor data streams. Receives data from WHOOP, Firstbeat, Spike, etc.

                          Re                                                               Relation
 Field         Type            Description
                          q                                                                s


 _id
               ObjectI
               d
                          ✅ MongoDB document ID                                            —



 user_id       string
                          ✅
                          🔑 🔗 Patient identifier
                                                                                           → patien
                                                                                           ts


 from_ts
               dateti
               me
                          ✅ Measurement
                            queries)
                                        period start (keyed for time-series
                                                                                           —
```

### Página 13

```text
Re                                                                    Relation
 Field        Type              Description
                        q                                                                     s

              dateti
 to_ts                  —       Measurement period end                                        —
              me

 source       string    —       Device/platform: whoop, firstbeat, spike, etc.                —

                                Nested sensor
 sensors      dict      —       data: heart_rate{value}, steps{value}, hrv, rmssd, recov      —
                                ery_score, etc.

 metada
              dict      —       Extension and source-specific raw payload                     —
 ta

Note: sensors.heart_rate is aggregated into daily min/avg/max series
by compute_heart_rate_daily_series().



🗺️ Body Charts
map_structinteg

Patient and clinician body-chart sessions (pain/stiffness point maps). "PainMapSession" is a
backward-compat alias.

                                        Re
 Field                      Type               Description                        Relations
                                        q

 _id                        ObjectId    ✅ MongoDB document ID                     —


 session_id                 string
                                        ✅
                                        🔑 Client-generated hex UUID               —


                                     ✅ 🔗
 user_id                    string
                                     🔑 Patient rut_norm / patient_id              → patients


                                       🔗 Associated Case (direct
 case_id                    ObjectId
                                     🔑 ObjectId since Mar 2026)
                                     —
                                                                                  → cases


 timestamp                  datetime
                                     ✅
                                     🔑 Session date/time                          —


 type                       string      ✅ patient_initial
                                          owup
                                                          or clinician_foll
                                                                                  —


 created_by                 string      ✅ patient or clinician                    —
```

### Página 14

```text
Re
 Field                    Type                Description                        Relations
                                       q

                                              [{ x, y, view, zone, painType,
 points
                          PainPoint
                          []
                                       ✅      size, painRating 0–10,
                                              stiffnessRating 0–10,
                                                                                 —
                                              psfsActivities[] }]

                                              { zones_affected[],
 summary                  dict         ✅      most_affected_zone,
                                              total_points,
                                                                                 —
                                              pain_distribution{} }

 exercises_recommen                           Exercise codes (eje_cod)           → ejercicios_catal
                          string[]     —
 ded                                          recommended for this session       ogo


 doctor_id                string       —
                                              🔗 Clinician who performed          → clinicians
                                              the assessment

                                              Snapshot of clinician name at
 doctor_name              string       —                                         —
                                              write time

                                              Free-text clinician notes for
 doctor_notes             string       —                                         —
                                              the session

 metadata                 dict         —      Extension fields                   —

Key indexes: user_id, session_id, timestamp, case_id



📅 Appointments & Notes
appointments

Scheduling entity for all patient appointments. Supports TM3, Nookal, and Cliniko sync.

                                 Re                                                          Relatio
 Field            Type                Description
                                 q                                                           ns

 _id              ObjectId  ✅ MongoDB document ID                                            —


                            🔑 🔗 Reference to patient
                  ObjectId| —                                                                → pati
 patient_id
                  string                                                                     ents


                                 🔑 🔗 Reference to episode of care
                  ObjectId|      —                                                           → case
 case_id
                  string                                                                     s
```

### Página 15

```text
Re                                                       Relatio
Field           Type            Description
                           q                                                        ns


                           🔑 🔗 Assigned clinician
                           —                                                        → clini
provider_id     ObjectId
                                                                                    cians


start_time      datetime
                           🔑 Appointment start
                           —
                                                                                    —


end_time        datetime   —    Appointment end                                     —

arrival_time    datetime   —    Recorded arrival time                               —


                           🔑
                           —    scheduled, confirmed, arrived, in_progress, compl
status          string                                                              —
                                eted, cancelled, no_show

cancellation_
                string     —    Reason if cancelled                                 —
reason

service_id      ObjectId   —    🔗 Booked service type                               —

appointment
                string     —    Initial, Follow-up, Group Class                     —
_type

is_group_ses
                bool       —    Whether this is a group/class appointment           —
sion

max_attende
                int        —    Max capacity for group sessions                     —
es

location_id     ObjectId   —🔗 Location reference                                    —


clinic_id
                ObjectId|
                string
                          — 🔗 Clinic (topbar selection)                             → clini
                                                                                    cs

room_id         any        —    Room or free-text location info                     —

is_telehealth   bool       —    Whether this is a virtual appointment               —

telehealth_u
                string     —    Video call link for telehealth sessions             —
rl

reason          string     —    Reason for appointment                              —
```

### Página 16

```text
Re                                                            Relatio
 Field           Type                Description
                               q                                                             ns

 contact_met
                 string        —     Dispatch method: app-notification, sms, email           —
 hod

 contact_ema
                 string        —     Override email if patient lacks one on file             —
 il

 alert_level     string        —     Priority: low, medium, high                             —

 notes           string        —     Free-text notes                                         —

 synced          bool          —     true once pushed/pulled from external system            —

 synced_at       datetime      —     Last successful sync timestamp                          —

 sync_source     string        —     External system: tm3, nookal, cliniko                   —

                                     ID in the external system (used for upsert
 external_id     string        —                                                             —
                                     matching)

 created_at      datetime      —     Creation timestamp                                      —

 updated_at      datetime      —     Last update timestamp                                   —

Key indexes: patient_id, provider_id, case_id, compound (start_time, end_time), status
Notifications: On create/edit/cancel, dispatches FCM push or SMS based on contact_method.
Logged to communications_log.



clinical_notes

SOAP and template-based clinical notes linked to a case and/or appointment.

 Field              Type                Req        Description                     Relations

 _id                ObjectId            ✅ MongoDB document ID                      —

                                        ✅ 🔗 Reference to patient (via
 patient_id         ObjectId
                                        🔑          Bunnet Link)
                                                                                   → patients


 provider_id        ObjectId            ✅ 🔗 Authoring clinician                    → clinicians

                                          🔗 Associated case
 case_id            ObjectId
                                        🔑 (optional)
                                        —
                                                                                   → cases
```

### Página 17

```text
Field                Type               Req      Description                     Relations

                                                  🔗 Associated appointment
                                         🔑
                                         —                                        → appointment
 appointment_id       ObjectId
                                                  (optional)                      s

 template_id          ObjectId           —        🔗 Template used (if any)        —


 template_name        string             ✅        Snapshot of the template
                                                  name at write time
                                                                                  —



 content              dict               ✅        Flexible SOAP or form JSON: {
                                                  S, O, A, P }
                                                                                  —


                      AttachmentRef[              [{ id, url, name }] linked
 attachments                             —                                        → media
                      ]                           images or PDFs

 is_draft             bool               —        true until finalised            —

 is_signed            bool               —        true after clinician signs      —

 signature_hash       string             —        Cryptographic signature hash    —

 created_at           datetime           —        Authoring timestamp             —

 updated_at           datetime           —        Last update timestamp           —

 finalized_at         datetime           —        Finalisation timestamp          —

Key indexes: patient_id, case_id, appointment_id, created_at



🏋️ Exercise System
ejercicios_catalogo

Master exercise catalog. 5,981 entries from Wibbi import (Apr 2026).

 Field                       Type       Req    Description

 _id                         ObjectId   ✅      MongoDB document ID


 exercise_id                 string
                                        ✅
                                        🔑      Internal exercise ID


 eje_cod                     string
                                        ✅
                                        🔑      Exercise code (unique)
```

### Página 18

```text
Field                  Type       Req   Description


eje_nom                string
                                  ✅
                                  🔑     Exercise name (unique, full-text indexed)


description            string     —     Short description

instructions           string[]   —     Step-by-step instructions

contraindications      string[]   —     Clinical contraindications

warnings               string[]   —     Safety warnings

equipment_needed       string[]   —     Required equipment

categories             string[]   —     Exercise categories

                                        Main anatomical
primary_zone           string     —
                                        zone: neck, shoulders, spine, hips, knees, ankles

target_zones           string[]   —     All applicable anatomical zones

difficulty             string     —     Difficulty level

suitable_for_severit
                       string[]   —     Target severity levels
y


tags                   string[]
                                  🔑
                                  —
                                        Searchable tags


external_ids           dict       —     External system mappings: { wibbi: "W-123" }

thumbnail_url          string     —     Exercise illustration URL

audio_path             string     —     GCS path to TTS audio file

video_path             string     —     Video demonstration path

sets                   string     —     Default sets

repetitions            string     —     Default repetitions

duration_seconds       int        —     Default duration

rest_seconds           int        —     Default rest between sets
```

### Página 19

```text
Field                      Type        Req      Description

 hold_seconds               int         —        Default hold time

 bilateral                  bool        —        Whether exercise is bilateral

 frequency                  string      —        Suggested frequency (e.g. "twice a day")

 popularity_score           int         —        Usage-based popularity ranking

 is_active                  bool        —        Whether visible in search results

 created_at                 datetime    —        Catalog entry creation timestamp

 updated_at                 datetime    —        Last update timestamp

Key indexes: eje_cod (unique), eje_nom (unique, text), tags, external_ids.wibbi



program_templates

Reusable ordered exercise pipelines. Globally available or scoped to a clinic/clinician.

 Field             Type                  Req     Description                     Relations

 _id               ObjectId              ✅       MongoDB document ID             —


 template_id       string
                                         ✅
                                         🔑
                                                 Internal standardised
                                                                                 —
                                                 template ID

                                                 External ID mappings: {
 template_ids      dict                  —                                       —
                                                 wibbi: "W-123" }


 name              string                ✅       Template display name
                                                 (full-text indexed)
                                                                                 —


                                                 Template purpose and
 description       string                —                                       —
                                                 clinical intent

                                                 🔗 Owning clinician (null = → clinicians
 clinician_id      string
                                         🔑
                                         —
                                                 global)

                                                 🔗 Owning clinic (null =
 clinic_id         string
                                         🔑
                                         —
                                                 global)
                                                                                 → clinics
```

### Página 20

```text
Field              Type                 Req     Description                       Relations

                                                 Ordered list: [{ exercise_id,
                                                 wibbi_id, sets, reps,
                                                                                   → ejercicios_catalog
 exercises          ProgramExercise[]    —       hold_seconds,
                                                                                   o
                                                 rest_seconds, frequency,
                                                 duration, other{} }]


                                         🔑
                                         —       Searchable tags for
 tags               string[]                                                       —
                                                 filtering

                                                 Whether available for
 is_active          bool                 —                                         —
                                                 assignment

 created_at         datetime             —       Creation timestamp                —

 updated_at         datetime             —       Last update timestamp             —

Key indexes: template_ids.wibbi, clinician_id, clinic_id, tags, name (full-text)



patient_programs

Active program assignment per patient. One active record per patient at a time.

 Field              Type        Req      Description                               Relations

 _id                ObjectId    ✅ MongoDB document ID              —


 patient_id         string
                                ✅
                                🔑 🔗 Patient identifier             → patients


                                ✅ 🔗 Array of assigned template IDs → program_template
 template_ids       string[]
                                🔑 (multi-program since Apr 2026) s
 created_at         datetime    —        Assignment timestamp                      —

 active_until       datetime    —        Expiry date; null = currently active      —

Key indexes: patient_id, template_ids, compound (patient_id, active_until)
Note: When a new program is assigned, existing active records are deactivated by setting active_until
= now.



clinical_programs

Patient-specific clinical programs (legacy; superseded by patient_programs + program_templates).
```

### Página 21

```text
Field                   Type                Req       Description                Relations


 _id                     ObjectId            ✅         MongoDB
                                                       document ID
                                                                                  —


 program_id              string              ✅         Internal program ID        —


                                             🔑
 wibbi_program_i                             —         Wibbi platform
                         string                                                   —
 d                                                     program ID

                                             ✅ 🔗 Patient
 patient_id              string
                                             🔑         identifier
                                                                                  → patients


                                             ✅ 🔗 Authoring
 clinician_id            string
                                             🔑 clinician                          → clinicians



 name                    string              ✅ Program
                                               name
                                                         display
                                                                                  —


 description             string              —         Program details            —

                                                       Exercise list with         → ejercicios_catalog
 exercises               ProgramExercise[]   —
                                                       parameters                 o

 start_date              datetime            —         Program start date         —

 end_date                datetime            —         Program end date           —

                                                       Whether currently
 is_active               bool                —                                    —
                                                       active



scheduled_exercises

Mobile app exercise schedule — which exercises to do on which days of the week.

 Field            Type            Req    Description                  Relations

 _id              ObjectId        ✅ MongoDB document ID —
 patient_id       string          ✅ 🔑 🔗 Patient identifier → patients
 id               string          —      Client-generated UUID        —


 exercise_id      string          —      🔗 Exercise reference         → ejercicios_catalog
                                                                      o
```

### Página 22

```text
Field             Type      Req          Description                 Relations

 name              string    —            Exercise display name       —

 sets              int       —            Number of sets              —

 reps              int       —            Number of repetitions       —

 day_of_week       int       —            1 (Mon) – 7 (Sun)           —

 is_recurring      bool      —            Repeats weekly              —

 is_active         bool      —            Currently scheduled         —



patient_routines

Custom workout routines created by patients in the mobile app.

 Field          Type                Req      Description                          Relations

 _id            ObjectId            ✅ MongoDB document ID                         —


 patient_id     string
                                    ✅
                                    🔑 🔗 Patient identifier                        → patients


 id             string              —        Client UUID                          —

 name           string              —        Routine name                         —

 description    string              —        Routine description                  —

                                             [{ exercise_id, order, sets,
                RoutineExercise[                                                  → ejercicios_catalog
 exercises                          —        reps, duration_seconds,
                ]                                                                 o
                                             rest_seconds }]

                                             Whether the routine is
 is_active      bool                —                                             —
                                             active



patient_workout_logs

Completed workout session logs from the mobile app.
```

### Página 23

```text
Field                Type                  Req    Description           Relations


 _id                  ObjectId              ✅ MongoDB
                                              ID
                                                       document
                                                                         —


 patient_id           string
                                            ✅
                                            🔑 🔗 Patient identifier       → patients


 id                   string                —      Client UUID           —


 routine_id           string                —
                                                   🔗 Routine performed → patient_routines
                                                   (if any)

                                                   Workout start
 started_at           datetime              —                            —
                                                   timestamp

                                                   Workout end
 completed_at         datetime              —                            —
                                                   timestamp

 notes                string                —      Session notes         —

                                                   [{ exercise_id,
                                                   sets_completed,
                                                                         → ejercicios_catalog
 exercises_logged     WorkoutExercise[]     —      reps_completed,
                                                                         o
                                                   weight_kg,
                                                   duration_seconds }]



patient_custom_exercises

Custom exercises created by patients, not in the main catalog.

 Field                   Type        Req        Description

 _id                     ObjectId    ✅ MongoDB document ID
 patient_id              string      ✅ 🔑 🔗 Patient identifier
 id                      string      —          Client UUID

 name                    string      —          Exercise name

 description             string      —          Exercise description

 muscle_group            string      —          Target muscle group
```

### Página 24

```text
Field                     Type         Req       Description

 equipment_needed          string       —         Required equipment

 is_active                 bool         —         Whether still active



🎯 Patient Goals & Engagement
patient_goals

Patient health and metric goals. One document per patient, upserted.

 Field            Type              Req       Description                                 Relations

 _id              ObjectId          ✅ MongoDB document ID                                 —


 patient_id       string
                                    ✅
                                    🔑 🔗 Patient identifier (unique)
                                                                                          → patient
                                                                                          s

                                              { exercise_target_count_week,
 health_goals     dict              —         sleep_target_hours_night,                   —
                                              stress_target_level }

                                              [{ metric_type, target_exercises_per_week
 metric_goals     MetricGoal[]      —                                                     —
                                              }]

 created_at       datetime          —         Creation timestamp                          —

 updated_at       datetime          —         Last update timestamp                       —

Key indexes: patient_id (unique)



patient_commitments

Gamification data: check-in streaks, streak freezes, achievements.

 Field                   Type        Req         Description                              Relations

 _id                     ObjectId    ✅           MongoDB document ID                      —


 patient_id              string
                                     ✅
                                     🔑           🔗 Patient identifier (unique)            → patient
                                                                                          s

 current_streak          int         —           Current consecutive check-in day count   —
```

### Página 25

```text
Field                   Type           Req       Description                                 Relations

 longest_streak          int            —         All-time best streak                        —

                                                  Streak freeze credits available (default:
 freezes_remaining       int            —                                                     —
                                                  2)

                                                  [{ used_at, recorded_at }] log of freeze
 freeze_history          dict[]         —                                                     —
                                                  uses

                                                  [{ type, unlocked_at, recorded_at
 achievements            dict[]         —                                                     —
                                                  }] earned badges

 created_at              datetime       —         Initialisation timestamp                    —

 updated_at              datetime       —         Last update timestamp                       —

Key indexes: patient_id (unique)



🔔 Alerts & Communications
alerts

Clinician-facing patient alerts. Merged with computed symptom trends in the dashboard.

 Field            Type            Req         Description                                Relations

 _id              ObjectId ✅ MongoDB document ID                                         —


 patient_id       string   ✅ 🔑 🔗 Patient identifier                                      → patient
                                                                                         s

 alert_type       string   ✅ 🔑 risk, review, watch, patient_assigned                     —

 created_at       datetime — 🔑 Alert creation timestamp                                  —


                  datetime — 🔑
                               When the alert was read by a
 read_at                                                                                 —
                               clinician

 action_take
 n
                  string          —   🔑       Description of the clinician action        —


 action_at        datetime        —           When the action was taken                  —

Key indexes: patient_id, alert_type, read_at, action_taken, created_at, compound (patient_id,
read_at)
```

### Página 26

```text
Dashboard: Unread alerts are merged with computed 5-day trend alerts and historial_medico status
to produce the unified dashboard alert list, sorted: Risk → Watch → Review.



communications_log

Outbound message log (email, SMS, FCM push). Intercepts all dispatch services.

 Field          Type         Req      Description                                   Relations

 _id            ObjectId     ✅        MongoDB document ID                           —


 patient_id     ObjectId     —        🔗 Associated patient (if known)               → patient
                                                                                    s

 recipient      string       ✅ 🔑 Phone number, email address, or user_id            —

 channel        string       ✅ email, sms, app-notification                         —


 status         int          ✅ 0accepted
                                  = sent to local queue; 1 = partner API
                                                                                    —


 metadata       dict         —        Exact payload snapshot at time of send        —

 created_at     datetime     —   🔑    Log entry creation timestamp                  —

 updated_at     datetime     —        Last status update timestamp                  —

Key indexes: recipient, created_at



actions_log

Administrative action audit trail. Records who did what and when.

 Field          Type         Req       Description                                  Relations

 _id            ObjectId     ✅ MongoDB document ID                                  —

 type           string       ✅ 🔑 Action type, e.g. patient.assign_clinician         —

                                       Contextual data (patient ID, clinician ID,
 metadata       dict         —                                                      —
                                       etc.)

 updated_at     datetime     —   🔑     Action timestamp                             —
```

### Página 27

```text
Field           Type         Req         Description                                 Relations

 updated_b
 y
                 string       —           🔗 User ID who performed the action          → usuario
                                                                                      s

 read_at         datetime     —   🔑       When the log entry was reviewed             —


 read_by         string       —           🔗 User ID who reviewed the entry            → usuario
                                                                                      s

Key indexes: type, read_at, updated_at, compound (metadata.care_clinician_id, read_at)



📋 Diagnostics
diagnostic_codes

ICD-10 or internal clinical diagnostic code catalog.

 Field           Type         Req        Description

 _id             ObjectId     ✅ MongoDB document ID
 diag_id         string       ✅ 🔑 Code identifier, e.g. M54.5
 diag_name       string       ✅ 🔑 Human-readable
                                  pain"
                                                     name, e.g. "Low back



 created_at      datetime     —          Record creation timestamp

 updated_at      datetime     —          Last update timestamp

Referenced by: cases.diagnosis_codes[]



diagnoses_sections

Groups diagnostic codes by anatomical section for the diagnostic assignment UI.

 Field           Type         Req      Description                             Relations

 _id             ObjectId     ✅        MongoDB document ID                     —


 section_id      string
                              ✅
                              🔑        Section slug, e.g. back, shoulder       —


 diag_ids        string[]     ✅ 🔗   List
                                of diagnostic_codes.diag_id values
                                                                               → diagnostic_code
                                                                               s
```

### Página 28

```text
Field           Type         Req          Description                                Relations

 created_at      datetime     —            Creation timestamp                         —

 updated_at      datetime     —            Last update timestamp                      —



⚙️ Admin & Config
state_rule_configs

Per-clinic patient status classification thresholds. Determines improving/stable/declining/at_risk
cutoffs.

 Field           Type                  Req       Description                                  Relations

 _id             ObjectId              ✅         MongoDB document ID                          —

 name            string                ✅         Human-readable configuration name            —

                                                 🔗 Scoped to this clinic; null = global
 clinic_id       string
                                       🔑
                                       —
                                                 default
                                                                                              → clinics



                               🔑       —         Whether this is the default config for the
 is_default      bool                                                                         —
                                                 clinic


 thresholds
                 RuleThreshold
                 s
                               ✅                 { improving, stable, declining, at_risk
                                                 } floor values (float)
                                                                                              —


 created_at      datetime              —         Creation timestamp                           —

 updated_at      datetime              —         Last update timestamp                        —


 created_by      string                —         🔗 User ID of creator                         → usuario
                                                                                              s

Referenced by: patients.active_rule_config_id



credentials

Encrypted third-party service credentials (WHOOP, Spike) per patient.

 Field                      Type           Req        Description                             Relations

 _id                        ObjectId       ✅          MongoDB document ID                     —
```

### Página 29

```text
Field                     Type        Req        Description                       Relations


 patient_id                string      ✅ 🔑 🔗 Patient identifier                     → patient
                                                                                    s

 connection_type           string      ✅ 🔑 Service type: whoop, spi, etc.           —

 username                  string      ✅ Third-party service login                  —

 password_encrypted        string      ✅ Fernet-encrypted password                  —

 connected_at              datetime    —          When connection was established   —

 last_used_at              datetime    —          Last successful use timestamp     —


 is_active                 bool        —   🔑      Whether the connection is still
                                                  active
                                                                                    —




legal_docs

Versioned legal documents (terms, privacy policy). Used during consent capture.

                               Re
 Field            Type                Description
                               q

 _id              ObjectId     ✅ MongoDB document ID
 type             string       ✅ Document type: tcon, privacy
 version          string       ✅ Version string, e.g. v2
 content          string       —      Full HTML or markdown content

 published_a
                  datetime     —      Publication timestamp
 t

Referenced by: consents.type + consents.version



🎟️ Support Tickets
ticket

Support and incident tickets with full Open → Closed lifecycle.
```

### Página 30

```text
Field                       Type            Req      Description             Relations


 _id                         ObjectId        ✅        MongoDB document
                                                      ID
                                                                              —


 title                       string          ✅        Ticket title            —

 description                 string          ✅        Issue description       —


 status                      string
                                             ✅
                                             🔑        Sent, Open, Closed      —


 reported_at                 datetime
                                             ✅
                                             🔑
                                                      When the ticket was
                                                                              —
                                                      filed

                                                      Resolution
 closed_at                   datetime        —                                —
                                                      timestamp


 reporter                    Participant     ✅        { name, email,
                                                      user_id }
                                                                              —



 category                    string          —        🔗 Category slug         → ticket_categorie
                                                                              s

 incident_type               IncidentType    —        { name, description }   —

                                                      🔗 Assigned
 responder_id                string
                                             🔑
                                             —
                                                      responder
                                                                              → responder


                                                      Resolution
 solution                    string          —                                —
                                                      description

 communication_channel       string          —        🔗 Channel used          → channels

 images                      string[]        —        Attachment URLs         → media

 metadata                    dict            —        Extension fields        —

Key indexes: reported_at, status, responder_id



ticket_categories

Taxonomy for ticket classification by campaign and category.
```

### Página 31

```text
Re
 Field            Type                    Description
                                  q

 _id              ObjectId        ✅ MongoDB document ID
 campaign         string          ✅ Campaign identifier
 category         string          ✅ Category slug
 name             string          —       Display name

 description      string          —       Category description



channels

Allowed communication channels for ticket routing.

                             Re
 Field         Type                    Description
                             q

 _id           ObjectId      ✅ MongoDB document ID
 channel       string        ✅ Channel name,
                               e.g. email, sms, chat



responder

Support desk responder accounts for ticket assignment.

                              Re
 Field          Type                    Description
                              q

 _id            ObjectId      ✅ MongoDB document ID
 name           string        ✅ Display name
 group          string        ✅ Team/group
 user           string        ✅ Login username
 password       string        ✅ Hashed password
email_template
```

### Página 32

```text
HTML email templates per campaign.

                              Re
 Field         Type                     Description
                              q

 _id           ObjectId       ✅ MongoDB document ID
 campaign      string         ✅ Campaign identifier
 subject       string         ✅ Email subject line
 title         string         ✅ Email heading title
 body          string         ✅ HTML body content
email_config

SMTP/IMAP configuration per campaign.

                                   Re
 Field             Type                   Description
                                   q

 _id               ObjectId        ✅ MongoDB document ID
 campaign          string          ✅ Campaign identifier
 email             string          ✅ Sender email address
 password          string          ✅ App password (encrypted)
 server_smt
 p
                   string          ✅ SMTP server hostname
 server_ima
 p
                   string          ✅ IMAP server hostname
 port              int             ✅ SMTP/IMAP port
email_infoticket

Ticket email body component parts per campaign.
```

### Página 33

```text
Re
 Field        Type                 Description
                           q

 _id          ObjectId     ✅ MongoDB document ID
 campaign     string       ✅ Campaign identifier
 header       string       ✅ Email header HTML
 body         string       ✅ Email body HTML
 footer       string       ✅ Email footer HTML
🖼️ Media
media

Generic registry for clinical videos, exercise images, and SVG anatomical diagrams.

 Field          Type         Req         Description

 _id            ObjectId     ✅           MongoDB document ID

 alt            string       —           Alt text / description

 url            string       —           Public access URL

 filename       string       —   🔑 Original filename
                                         MIME type,
 mime_type      string       —
                                         e.g. video/mp4, image/svg+xml

 filesize       float        —           File size in bytes

 width          float        —           Image/video width in px

 height         float        —           Image/video height in px

 created_at     datetime     —           Upload timestamp

 updated_at     datetime     —           Last update timestamp

Key indexes: alt, filename, created_at



Cross-Collection Relationship Map
```

### Página 34

```text
usuarios ──────────────────────────────────────────────►
invitations

 │                              push_tokens

 │

 ├── (patient_id) ──────────────────────────────────► patients

 │                                │

 │
┌──────────────┼─────────────────────────────────────────
─┐

 │                      ▼            ▼                          ▼

 │                     cases      checkins                  map_structinteg

 │                      │        (user_id)                  (user_id, case_id)

 │                      │

  │                     ├──► appointments ──────────────────────────►
communications_log

 │                      │      (case_id, provider_id, clinic_id)

 │                      │

 │                      └──► clinical_notes ──► attachments ──────────► media

 │                             (case_id, appointment_id, provider_id)

 │

 └── (clinician_id) ─────────────────────────────────► clinicians

                                 │

                        ┌─────────────┼─────────────────┐

                        ▼          ▼           ▼

                      clinics program_templates alerts

                     (clinic_ids) (clinician_id) (patient_id)



patients
─────────────────────────────────────────────────────────
─────────────────────────────────────►

 │ ├── cases ──► appointments, clinical_notes, map_structinteg

 │ ├── intakes

 │ ├── consents
```

### Página 35

```text
│ ├── historial_medico           (1:1)

  │ ├── patient_goals           (1:1)

  │ ├── patient_commitments             (1:1)

  │ ├── patient_programs
──────────────────────────────────────────────────►
program_templates

  │ │     │                                     │

 │ │
└────────────────────────────────────────────────────────
──────► ejercicios_catalogo

  │ ├── checkins

  │ ├── metrics

  │ ├── credentials

  │ ├── alerts

  │ ├── communications_log

  │ ├── scheduled_exercises
──────────────────────────────────────────────►
ejercicios_catalogo

  │ ├── patient_routines
─────────────────────────────────────────────────►
ejercicios_catalogo

 │ └── patient_workout_logs
──────────────────────────────────────────────► patient_routines



diagnostic_codes ◄────────────────────────── diagnoses_sections

  ▲

  └───────────────────────────────────────── cases.diagnosis_codes[]



state_rule_configs ◄────────── patients.active_rule_config_id

  │

  └──► clinics (scoped by clinic_id)



Quick Lookup: Field → Collection
```

### Página 36

```text
Looking for...            Check collection      Field

Patient by phone          patients              contact.phone

Patient by email          patients              contact.email

Patient by TM3 ID         patients              ids.tm3

Patient's primary
                          patients              care_clinician_id → clinicians._id
clinician

Patient's active
                          patient_programs      patient_id + active_until = null
program

Patient's check-in
                          checkins              user_id (= patient_id)
history

Clinician's TM3
                          clinicians            ids.tm3
practitioner ID

Appointment by
                          appointments          external_id
external TM3 ID

Latest patient status     historial_medico      paciente_id → estado_act.est_act_nom

Unread clinician alerts   alerts                patient_id + read_at = null

FCM device tokens         push_tokens           user_id + is_active = true

Active WHOOP                                    patient_id + connection_type =
                          credentials
credentials                                     "whoop" + is_active = true

Exercise by Wibbi ID      ejercicios_catalogo   external_ids.wibbi

Program template by
                          program_templates     template_ids.wibbi
Wibbi ID
```