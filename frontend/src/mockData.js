export const mockQueries = [
  {
    id: 'medical',
    title: 'Medical Diagnosis',
    tag: 'Healthcare',
    question: 'How should a 64-year-old with chest pain and shortness of breath be triaged?',
    result: {
      scores: {
        overall: 6,
        data_sufficiency: 5,
        reasoning_certainty: 6,
        justification: 'Limited clinical context means the diagnosis is plausible but not definitive.'
      },
      gaps: [
        'No vital signs or ECG data were provided.',
        'Potential differential diagnoses like pulmonary embolism or aortic dissection are not excluded.',
        'Unknown patient history for heart disease, medication use, or recent trauma.'
      ],
      calibrated_response:
        'The current data suggests a high-risk cardiopulmonary event; immediate emergency evaluation is warranted, but the exact cause cannot be confirmed without imaging and vital signs.',
      resolutions: [
        'Obtain ECG and troponin values immediately.',
        'Collect full past medical history and medication list.',
        'Perform chest imaging to rule out acute pulmonary embolism or aortic injury.'
      ]
    }
  },
  {
    id: 'legal',
    title: 'Legal Sentencing',
    tag: 'Regulation',
    question: 'What is the most likely sentence for a first-time offender convicted of felony fraud in California?',
    result: {
      scores: {
        overall: 5,
        data_sufficiency: 4,
        reasoning_certainty: 5,
        justification: 'Key jurisdictional details and offense severity are missing, so conclusions remain tentative.'
      },
      gaps: [
        'Actual loss amount and victim impact are unknown.',
        'Whether the defendant accepted a plea deal or has mitigating factors is unclear.',
        'California sentencing guidelines vary widely by felony class and prior history.'
      ],
      calibrated_response:
        'A plausible outcome is probation with fines for lower-level fraud, but significant custodial time or restitution is possible depending on loss amount and judicial discretion.',
      resolutions: [
        'Verify the statutory felony classification and loss threshold.',
        'Check whether the court accepted a plea agreement or diversion program.',
        'Gather defendant history and aggravating or mitigating circumstances.'
      ]
    }
  },
  {
    id: 'engineering',
    title: 'Structural Engineering',
    tag: 'Infrastructure',
    question: 'Is a single-span steel beam sufficient for a 50-foot pedestrian bridge in a coastal environment?',
    result: {
      scores: {
        overall: 4,
        data_sufficiency: 3,
        reasoning_certainty: 4,
        justification: 'Without load values or environmental specs, the design conclusion is highly uncertain.'
      },
      gaps: [
        'Live load, wind load, and corrosion factors are not defined.',
        'Material grade and beam cross-section details are missing.',
        'Coastal salt exposure and maintenance plan are not available.'
      ],
      calibrated_response:
        'It may be feasible with a properly graded steel section, but the design cannot be confirmed until structural loads and environmental protections are specified.',
      resolutions: [
        'Perform a load analysis including pedestrian, wind, and seismic forces.',
        'Specify steel grade, corrosion protection, and section modulus.',
        'Review local coastal codes for durability and maintenance requirements.'
      ]
    }
  }
]
