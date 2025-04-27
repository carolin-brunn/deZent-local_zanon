import pandas as pd

import zanon_utils as z_utils
import logging_utils as logger

from logging_utils import RecordLog, PubLog, PubLogEntry, SimuLog


class CentralEntity():
    def __init__(self):
        #self.env = env
        ##self.zanon = zanon
        self.clock = 0
        self.id = "CE"

        self.record_log = RecordLog() #{} # record value = key, per record remember occurrence with [sm_log] = time_log (only keep newest occurrence per sm) oder TODO: mit RecordLogEntry umsetzen
        self.pub_records = PubLog()#pd.DataFrame(columns = ["key", "orig_measurement", "GW", "time", "ID", "type"])
        self.simu_log = SimuLog()

    '''
        update central record log with data reported by GW
    '''
    def update_central_record_log(self, gw_record_log, curr_time):
        for m_key in gw_record_log:
            for sm_id, log_entry in gw_record_log[m_key].items():
                if(log_entry.time == curr_time):
                    self.record_log.add_new_m_to_record_log(log_entry.orig_measurement, m_key, sm_id, log_entry.sm_type, log_entry.time )
            

    # TODO: same function as for GWs with p_pub == 100?!
    """
    def publish_anonyimzed_tuples(self, cnt_struct, curr_time):
        l_pub_records = []
        #print("__pub round__: complete record_log:")
        #self.record_log.print_record_log()
        l_pub_records = self.get_curr_records_for_publishing(cnt_struct, curr_time)

        # key hashes of some of GW's records were found in cnt_struct
        if(l_pub_records):
            # try to publish the newest entries first
            for rec2pub in reversed(l_pub_records):
                if(cnt_struct.check(rec2pub.key)):
                    #("__pub round__: publish record ", rec2pub)
                    # publish PubLogEntry entry to CE with value, timepoint, and sm_id for collection and further processing
                    self.publish_tuple(rec2pub, self.id)
                    
                    # update flag in record_log to indicate that the corresponding tuple has been published (pr == PubLogEntry)
                    self.record_log.update_local_record_log(rec2pub)

                    # remove element from bloomfilter
                    cnt_struct.remove(rec2pub.key) 
                    #print("__pub round__: updated CBF after removing entry at GW ", self.id)
                    #cnt_struct.print_cnt_struct()
                # count structure is empty after publication -> not often the case
                if(cnt_struct.is_empty()):
                    break
        return cnt_struct
    """

    def cnt_curr_values(self):
        # NOTE: only logs that might be counted (== within dt) in record log
        df_record = pd.DataFrame.from_records(
            [
                (m_key, sm_id, l_entry.orig_measurement, l_entry.time, l_entry.is_published)
                for m_key, level2_dict in self.record_log.log.items()
                for sm_id, l_entry in level2_dict.items()
             ],
             columns = ["measurement", "SM", "orig_val", "time", "is_published"])
        # TODO: eiegntlich brauche ihc nur m_key und sm_id
        df_cnt = df_record.groupby("measurement").size().reset_index().rename(columns={0:'tuple_count'})
        #print(df_cnt.head())
        return df_cnt

    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct, curr_time):
        # find out which of the records in my local log are in cnt_struct, meaning they occurred at more than z individuals
        #existing_record_keys = cnt_struct.existing_records(self.record_log.log.keys())
        existing_record_keys = [x for x in cnt_struct["measurement"]] #cnt_struct.keys()
        
        l_pub_records = []
        #print("__check__: existing records: ", existing_record_keys)

        # get those entries that are from the current round (timepoint) and could get published
        for m_key in existing_record_keys:
            curr_entry = self.get_entries_w_current_timestamp(m_key, curr_time)
            if(curr_entry):
                l_pub_records.extend(curr_entry)
        #print("__check__: potential current pub records at GW: ", self.id)
        #logger.print_pub_log(pub_records)
        #print(l_pub_records)
        # publish newest tuples first
        l_pub_records.reverse()
        return l_pub_records

    '''
        return PubLogEntry Entry with current timestamp
    '''
    def get_entries_w_current_timestamp(self, m_key, curr_time):
        curr_records = []
        for sm_id, log_entry in self.record_log.log[m_key].items():
            if( (log_entry.time == curr_time) and (not log_entry.is_published) ):
                new_pub_log = PubLogEntry(m_key, log_entry.orig_measurement, log_entry.time, sm_id, log_entry.sm_type)
                curr_records.append(new_pub_log)
        return curr_records
    

    def publish_tuple(self, pub_log):
        #new_record = pd.DataFrame({"value": [pub_log.key], "time": [pub_log.time], "ID": [pub_log.id], "orig_measurement": [pub_log.measurement], "type": [pub_log.sm_type]})
        #self.pub_records.log = pd.concat([self.pub_records.log, new_record], ignore_index = True) # Appending new rows using concat()
        self.pub_records.add_new_tuple(pub_log)

    def store_tuple_in_simu_log(self, tuple):
        self.simu_log.add_new_tuple(tuple)



    """
    def get_curr_gw_records(self, gw_record_log, curr_time):
        curr_records = []
        #for key, log in gw_record_log.items():
        for key in gw_record_log:
            for sm_id, log_entry in gw_record_log[key].items():
                if(log_entry.time == curr_time):
                    curr_records.append({key: gw_record_log[key]})
            #for sm_id, log_entry in tmp_record.items():
                
        return curr_records
    """

    """
        update record that has been published and set flag to avoid publishing multiple times
            pub_tuple == PubLogEntry
    """
    """
    def update_local_record_log(self, pub_tuple):
        is_published = True
        self.record_log[pub_tuple.key][pub_tuple.id] = RecordLogEntry(pub_tuple.value, pub_tuple.sm_type, pub_tuple.time, is_published)
        return"
    """