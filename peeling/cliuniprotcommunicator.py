from peeling.uniprotcommunicator import UniProtCommunicator


class CliUniProtCommunicator(UniProtCommunicator):

    # implement abstract method
    async def get_latest_id(self, old_ids):
        meta={}
        return await self._retrieve_latest_id(old_ids, meta)
