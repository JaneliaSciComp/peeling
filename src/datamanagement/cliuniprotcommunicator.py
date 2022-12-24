from datamanagement.uniprotcommunicator import UniProtCommunicator


class CliUniProtCommunicator(UniProtCommunicator):
    
    # overriding abstract method
    def get_latest_id(self, old_ids):
        return self._retrieve_latest_id(old_ids)
