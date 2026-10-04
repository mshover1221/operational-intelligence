class Claim:
    def __init__(self, entity, attribute, value, evidence, claim_type="assertion"):
        self.entity = entity
        self.attribute = attribute
        self.value = value
        if isinstance(evidence, list):
            self.evidence = evidence
        else:
            self.evidence = [evidence]
        self.claim_type = claim_type
