class InterpretationResult:
    def __init__(self, evidence, claims):
        self.evidence = evidence
        self.claims = claims

        if claims:
            self.status = "claims_extracted"
        else:
            self.status = "insufficient_support"
