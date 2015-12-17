class InputFiles:
    def __init__(self, plink_prefix, pair_path, cov_path = None, pheno_path = None, info_path = None):
        self.plink_prefix = plink_prefix
        self.pair_path = pair_path
        self.cov_path = cov_path
        self.pheno_path = pheno_path
        self.info_path = info_path
