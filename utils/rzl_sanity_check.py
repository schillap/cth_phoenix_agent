from sanity_checker import SanityCheck, CheckResult, CheckStatus
import os

class IDPPEnableCheck(SanityCheck):

    """Validates IDPP is enabled in the Phoenix run setup"""
    
    def __init__(self):
        super().__init__(
            "IDPP Enable Check",
            "Validates IDPP is enabled in the Phoenix run setup")
        
    
    def execute(self, ward_path: str, block_name:str , tech:str, **kwargs) -> CheckResult:
        
        try:
            self.logger.debug(f"Checking IDPP enablement in: {ward_path}")
            log_list_to_check = kwargs.get('log_list_to_check')

            if log_list_to_check is not None:
                for log in log_list_to_check:
                    idpp_file = os.path.join(f"{ward_path}/runs/{block_name}/{tech}/{kwargs.get('apr_fc_dir')}/logs/fc.{log}")
                    
                    if not os.path.exists(idpp_file):
                        self.logger.warning(f"Log file {idpp_file} does not exist")
                        return CheckResult(
                            self.name,
                            CheckStatus.FAILED,
                            f"Log file {idpp_file} does not exist"
                        )
                    
                    with open(idpp_file,"r") as file:
                        if "PrimePower FINISHED" not in file.read():
                            self.logger.warning(f"'PrimePower FINISHED' not found in {idpp_file}")
                            print(f"'PrimePower FINISHED' not found in {idpp_file}, Please check IDPP is correctly enabled in you reference run.")
                            return CheckResult(
                                self.name,
                                CheckStatus.FAILED,
                                f"'PrimePower FINISHED' not found in {idpp_file}, Please check IDPP is correctly enabled in you reference run."
                            )
                        else:
                            self.logger.info(f"'PrimePower FINISHED' found in {idpp_file}")
                            print(f"IDPP Enabled in {idpp_file}")
                            return CheckResult(
                                self.name,
                                CheckStatus.PASSED,
                                f"'PrimePower FINISHED' found in {idpp_file}"
                            )
            
        except Exception as e:
            self.logger.exception(f"Exception in {self.name}")
            return CheckResult(
                self.name,
                CheckStatus.FAILED,
                f"Exception occurred: {str(e)}"
            )
        
        # Default return if no other conditions are met
        return CheckResult(
            self.name,
            CheckStatus.FAILED,
            "IDPP enablement check did not complete successfully"
        )

class PowerCollateralCheck(SanityCheck):
    """Validates power collateral files exists"""
    
    def __init__(self):
        super().__init__(
            "Power Collateral Check",
            "Validates power collateral files exist")
        
    
    def execute(self, ward_path: str, block_name:str , tech:str,**kwargs) -> CheckResult:
        
        try:
            self.logger.debug(f"Checking power collateral files in: {ward_path}")
            file_path = os.path.join(f"{ward_path}/runs/{block_name}/{tech}/release/latest")
            
            
            if not os.path.exists(file_path):
                self.logger.warning(f"Missing power collateral file: {file_path}")
                return CheckResult(
                    self.name,
                    CheckStatus.FAILED,
                    f"Missing power collateral file: {file_path}"
                )
            
            
            self.logger.info("Power collateral file is present")
            return CheckResult(
                self.name,
                CheckStatus.PASSED,
                "All power collateral files present"
            )
        except Exception as e:
            self.logger.exception(f"Exception in {self.name}")
            return CheckResult(
                self.name,
                CheckStatus.FAILED,
                f"Exception occurred: {str(e)}"
            )

class R2RTNSQoRCheck(SanityCheck):
    """Validates R2RTNS values is greater than threashold"""
    
    def __init__(self):
        super().__init__(
            "R2RTNS Check",
            "Validates R2RTNS values is greater than threashold")
        
    
    def execute(self, ward_path: str, block_name:str , tech:str, **kwargs) -> CheckResult:
        try:
            self.logger.debug(f"Checking R2RTNS value: {ward_path}")
            file_path = os.path.join(f"{ward_path}/runs/{block_name}/{tech}/{kwargs.get('apr_fc_dir')}/reports/compile_final_opto/{kwargs.get('report_file')}")
            
            
            if not os.path.exists(file_path):
                print("Missing Report file")
                self.logger.warning(f"Missing Report file: {file_path}")
                return CheckResult(
                    self.name,
                    CheckStatus.FAILED,
                    f"Missing Report file: {file_path}"
                )
            
            # Read the file and extract R2RTNS value
            with open(file_path,"r") as file:
                content = file.read()
                
                # Look for the Setup violations section
                if "Setup violations" not in content:
                    print("R2RTNS Values not found in report")
                    self.logger.warning("R2RTNS Values not found in report")
                    return CheckResult(
                        self.name,
                        CheckStatus.FAILED,
                        "R2RTNS Values not found in report"
                    )
                
                # Find the TNS line
                for line in content.split('\n'):
                    if line.strip().startswith('TNS'):
                        # Split by whitespace and extract columns
                        parts = line.split()
                        if len(parts) >= 3:
                            reg_to_reg_tns = abs(float(parts[2]))  # reg->reg is the 3rd column
                            self.logger.info(f"Found R2RTNS value: {reg_to_reg_tns}")
                            
                            # You can add threshold check here
                            threshold = kwargs.get('tns_threshold', -50e-9)  # Default threshold
                            print(threshold)
                            print((reg_to_reg_tns))
                            if reg_to_reg_tns > threshold:
                                return CheckResult(
                                    self.name,
                                    CheckStatus.FAILED,
                                    f"R2RTNS Value: {reg_to_reg_tns} is above threshold {threshold}"
                                )
                            
                            return CheckResult(
                                self.name,
                                CheckStatus.PASSED,
                                f"R2RTNS Value: {reg_to_reg_tns} is acceptable"
                            )
                
                self.logger.warning("R2RTNS not found")
                return CheckResult(
                    self.name,
                    CheckStatus.FAILED,
                    "R2RTNS not found"
                )
            
        except Exception as e:
            self.logger.exception(f"Exception in {self.name}")
            return CheckResult(
                self.name,
                CheckStatus.FAILED,
                f"Exception occurred: {str(e)}"
            )

