#import simpy
import random
#import numpy as np

#import zanon_utils as z_utils
import logging_utils as logger
from logging_utils import RecordLog, PubLogEntry, SimuLogEntry

#from counting_bloom_filter import CBloomFilter
from smartmeter import SmartMeter
from profile_distribution import ProfileDistribution



class Gateway():
    def __init__(self, ce, id=None,n_sm_conn=0):
        #self.env = env
        #self.zanon = zanon
        self.ce = ce

        self.id = id
        self.gw_pred = None
        self.gw_suc = None
        
        self.n_sm_conn = n_sm_conn
        self.gw_type = "standard" # mieter # industry
        self.profile_type = "tk" # "berlin", "ger"

        self.l_sms = {} # TODO: remember sm id and instance
        self.record_log = RecordLog()#{} # TODO: record value = key, per record remember occurrence with [sm_log] = time_log (only keep newest occurrence per sm) oder TODO: mit RecordLogEntry umsetzen

        self.coord_noise = 0
        self.gw_ce_msg_cnt = 0

##########################
##### SETUP #####
##########################
    '''
        connect GW with smart meters
            for now this is done for all connections that are available
    '''
    def connect_gw_to_sm(self):
        sm_distribution = ProfileDistribution()
        sm_distribution.generate_sm_weighted_distribution(self.profile_type, self.gw_type)

        #print("__connect GW SM__: ", self.n_sm_conn, " smart meters for GW no. ", self.id)

        for conn in range(self.n_sm_conn):
            sm = SmartMeter( sm_distribution, sm_id=conn, gw_id=self.id)#SmartMeter(self.env, sm_distribution, sm_id=conn, gw_id=self.id)
            if sm.id not in self.l_sms.keys():
                self.l_sms[sm.id] = sm # list with sms connected to GW
        #print("__connect GW SM__: added SM ", self.l_sms)


##########################
##### COLLECTION ROUND #####
##########################
    '''
        coordinating gw prepares and starts collection round
            create cbf and add initial noise for protecting measurement entries
    '''
    def add_initial_noise_to_cnt_struct(self, cnt_struct):
        self.coord_noise = random.randint(20,30)
        cnt_struct.add(self.coord_noise)
        #print("__coord add_init_noise__: adding random initial noise to CBF: ")
        #cnt_struct.print_cnt_struct()
        return cnt_struct
    
    
    '''
        remove initial noise before preoceeding to data publication
    '''
    def remove_initial_noise_from_cnt_struct(self, cnt_struct):
        cnt_struct.remove(self.coord_noise)
        #("__coord remove_init_noise__: removing random initial noise: ")
        ##cnt_struct.print_cnt_struct()
        return cnt_struct


    '''
        collection round with count structure passed on from predecessor
    '''
    def add_curr_measurement(self, cnt_struct, curr_time):
        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_time)

        # add valid measurements (wihtin delta t) of all SMs connected to this GW to count structure
        cnt_struct.add_measurements(self.record_log.log)
        #print("__data collection__: added measurements at GW: ", self.id)
        #cnt_struct.print_cnt_struct()
        return cnt_struct


    '''
        get new measurement for the current time point from sm and add to list
            save values in dictionary for smart meters with measurements and time point
    '''
    def collect_curr_measurement_from_sms(self, curr_time):
        #print("__new request m__: at GW ", self.id)
        for sm_id in self.l_sms.keys():
            # get sm instance to request current measurement
            sm = self.l_sms[sm_id]
            curr_measurement, m_key = sm.measure_data(curr_time)

            # add measurement to log at GW
            self.record_log.add_new_m_to_record_log(curr_measurement, m_key, sm_id, sm.type, curr_time)

            # record all occurred tuple for simulation analysis
            #   NOTE: this would not be done for "real" z-anonymity
            log_tuple = SimuLogEntry(m_key, curr_measurement, curr_time, sm_id, sm.type)
            self.ce.store_tuple_in_simu_log(log_tuple)

        #print("record log at GW: ", self.id)
        #self.record_log.print_record_log()


##########################
##### PUBLICATION ROUND #####
##########################
    """
    def publish_anonyimzed_tuples(self, cnt_struct, p_pub, curr_time):
        l_pub_records = []
        #("__pub round__: complete record_log:")
        #self.record_log.print_record_log()
        l_pub_records = self.get_curr_records_for_publishing(cnt_struct, curr_time)

        # key hashes of some of GW's records were found in cnt_struct
        if(l_pub_records):
            for rec2pub in l_pub_records:
                # take publication responsibility with p_pub 
                rnd = random.randint(0,100)
                #print("__pub_round__: my rnd ", rnd, ", p_pub: ", p_pub)
                if(rnd <= p_pub):
                    if(cnt_struct.check(rec2pub.key)):
                        #print("__pub round__: publish record ", rec2pub)
                        # to publish: forward PubLogEntry to CE with value, timepoint, and sm_id for collection and further processing
                        self.ce.publish_tuple(rec2pub, self.id)

                        # update flag in record_log to indicate that the corresponding tuple has been published (rec2pub == PubLogEntry)
                        self.record_log.update_local_record_log(rec2pub)

                        # remove element's hash from cnt_struct
                        cnt_struct.remove(rec2pub.key) 
                        #print("__pub round__: updated CBF after removing entry at GW ", self.id)
                        #cnt_struct.print_cnt_struct()

                    # count structure is empty after publication -> not often the case due to older measurements within dt that are also counted
                    if(cnt_struct.is_empty()):
                        break
        return cnt_struct
    """


    '''
        get list of PubLogEntry Entries that have been counted more than z times for publishing
            only publish those entries that have been recorded in current clock cycle
    '''
    def get_curr_records_for_publishing(self, cnt_struct, curr_time):
        # find out which of the records in my local log are in cnt_struc t, meaning they occurred at more than z individuals
        existing_record_keys = cnt_struct.existing_records(self.record_log.log.keys())
        pub_records = []
        #print("__check__: existing records: ", existing_record_keys)
        # get those entries that are from the current round (timepoint) and could get published
        for m_key in existing_record_keys:
            curr_entry = self.get_entries_w_current_timestamp(m_key, curr_time)
            if(curr_entry):
                pub_records.extend(curr_entry)
        #print("__check__: potential current pub records at GW: ", self.id)#, pub_records)
        #logger.print_pub_log(pub_records)
        return pub_records
    
    
    '''
        return PubLogEntries with current timestamp
    '''
    def get_entries_w_current_timestamp(self, m_key, curr_time):
        curr_records = []
        for sm_id, log_entry in self.record_log.log[m_key].items():
            if( (log_entry.time == curr_time) and (not log_entry.is_published) ):
                new_pub_log = PubLogEntry(m_key, log_entry.orig_measurement, log_entry.time, sm_id, log_entry.sm_type)
                curr_records.append(new_pub_log)
        return curr_records
    
    
    
    def publish_tuple(self, tuple):
        self.ce.publish_tuple(tuple)
        self.gw_ce_msg_cnt += 1



    def get_gw_ce_msg_cnt(self):
        tmp_cnt = self.gw_ce_msg_cnt
        self.gw_ce_msg_cnt = 0
        return tmp_cnt
    

##########################
##### OLD SNIPPETS #####
##########################
    """
    def coord_init_collection_round(self, curr_time, cnt_struct):
        # create structure for counting and data exchange
        #cnt_struct = z_utils.create_cnt_structure(self.n_sm_conn, self.zanon.n_cycles_for_anon, self.struct_type)
        #if(cnt_struct.is_empty()):
        #    print("__coord_collect__: created empty CBF")

        # add random noise to count structure
        self.coord_noise = cnt_struct.generate_initial_noise()
        print("__coord collect__: starting CBF with noise: ")
        z_utils.print_cnt_struct(cnt_struct)
        

        # send message to successor to start collection round
        #self.gw_suc.collection_round(self.id, cnt_struct, curr_time)
    """
        

    '''
        add sm and time info to record_log dictionary at key = curr_measurement
    '''
    """
    def add_new_m_to_record_log(self, curr_measurement, m_key, sm_id, sm_type, t):
        # new measurement -> cannot have been published yet
        is_published = False
        # measurement value was already observed at some SM before -> either add (sm: t) newly or update t for this observation at this SM
        if(m_key in self.record_log):
            self.record_log[m_key][sm_id] = RecordLogEntry(curr_measurement, sm_type, t, is_published)

        # measurement value has never been seen before -> add to dictionary
        else:
            self.record_log[m_key] = {sm_id: RecordLogEntry(curr_measurement, sm_type, t, is_published)}
    """

    '''
        ongoing collection round with count structure passed on from predecessor
    '''
    """
    #def collect_curr_measurement(self, coord_id, cnt_struct, curr_time):
    def collect_curr_measurement(self, cnt_struct, curr_time):
        # delete measurements that are not within delta_t anymore
        #self.apply_deltat_to_records(curr_time)
        #self.record_log = z_utils.apply_deltat_to_records(self.record_log, curr_time, self.zanon.delta_t)

        # get measurement from smart meters connected to gw
        self.collect_curr_measurement_from_sms(curr_time)

        # add valid measurements (wihtin delta t) of all SMs connected to this GW to count structure
        cnt_struct.add_measurements(self.record_log)
        print("__data collection__: added measurements at GW: ", self.id)
        z_utils.print_cnt_struct(cnt_struct)
        return cnt_struct
        if(coord_id == self.id):
            # round has been completed and cnt_struct is back at start point
            print("__collection round__: back at coord ", self.id)
            z_utils.print_cnt_struct(cnt_struct)

            # remove initial noise to not skew counting
            cnt_struct.remove_inital_noise(self.coord_noise)
            print("__data collection__: removed init noise: ")
            z_utils.print_cnt_struct(cnt_struct)

            self.coord_return_collection_result(cnt_struct, curr_time)

        else:
            # forward cbf to successor
            self.gw_suc.collection_round(coord_id, cnt_struct, curr_time)
        """


    '''
        after completing the collection round: coordinating GW returns cnt_structure
            from there start coord_publication round with specified p_pub on coord_gw 
            #   (for better visibility and understanding of algorithm)
            # functionality can also be moved directly to this point
    '''
    """
    def coord_return_collection_result(self, cnt_struct, curr_time):
        self.zanon.ensure_min_cnt(self, cnt_struct, curr_time)
    """

    '''
        create cbf for data collection
    '''
    """
    def create_cnt_structure(self):
        # n: number of expected items -> estimate number of items that occur within delta_t at all the gateways
        # n = no. of items = #(GWs) * #(SM p. GW) * (dt/f)
        # NOTE: this creates a varying n depending on the current round coordinator since n_sm_conn vaires btw GWs
        # This is deliberately accepted in the expectation that collisions with underestimated n 
        #   will balance out over time due to overestimated Bloom filters with other round coordinating GWs
        n = 10 * self.n_sm_conn * self.zanon.n_cycles_for_anon  

        # N: size of each counter in the bucket
        # 2^N occurrences can be counted
        N = 5  

        # m: total number of the buckets in the filter
        # this can be estimated by setting desired false positive rate P
        # m = (-n*ln(P))/(ln(2)^2)
        P = 0.05
        m_est = int( (-n*np.log(P)) / (np.log(2)**2) )
        m = min(m_est, 1000) # cut max number of buckets # TODO

        # k: number of hash functions
        # K = (m/n) * ln(2)
        k_est = int( (m/n) * np.log(2) )
        k = max(1, k_est)
        k = min(k, 6) # use between 1 and 6 hash functions
        
        match self.struct_type:
            case "bloom":
                cnt_struct = CBloomFilter(n, N, m, k)

        return cnt_struct
    """


    '''
        delete measurements from timepoints older than delta_t 
            update local record list to keep only valid data points 
    '''
    """ TODO: move to z_utils
    def apply_deltat_to_records(self, curr_time):
        t_limit = curr_time - self.zanon.delta_t # t_limit = datetime <= curr_time = datetime delta_t = time_delta
        print("__apply dt__: curr_time: ", curr_time, " dt: ", self.zanon.delta_t, " limit: ", t_limit)

        print("__apply dt__: at GW ", self.id, " pre record log: ")
        self.print_record_log()

        l_del_rec = []

        # for each record get log entries
        for record_val in self.record_log.keys():
            l_del_sm = []
            for sm_id, log_entry in self.record_log[record_val].items():
                if(log_entry.time < t_limit):
                    l_del_sm.append(sm_id)

            # delete observations of SMs that are too old
            for del_sm in l_del_sm:
                del self.record_log[record_val][del_sm]
                # no entries left for this record value
                if(not self.record_log[record_val]):
                    l_del_rec.append(record_val)
                    
        for del_rec in l_del_rec:           
            del self.record_log[del_rec]
        
        print("__apply dt__: at GW ", self.id, " post record log: ")
        self.print_record_log()
    """
    '''
        print record log at GW for debugging
    '''
    """
    def print_record_log(self):
        for i in self.record_log.keys():
            for sm, log_entry in self.record_log[i].items():
                print("__record log__: GW: ", self.id, " measurement_key: ", i, ", SM: ", sm, log_entry)
    """
    '''
        coordinating gw prepares and starts publication round
            clean cbf and then start publication round in ring by forwarding count structure to successor
    '''
    """
    def coord_publication_round(self, cnt_struct, init_p_pub, first_pub_trigger, curr_time):
        print("__coord publication__")
        if(first_pub_trigger):
            #print("__coord pub round__: initial CBF: ", cnt_struct.bit_array)
            p_pub = init_p_pub
            # start first publication round 
            self.gw_suc.publication_round(self, cnt_struct, p_pub, curr_time) # pass gw_coord along

        else:
            # second_round
            # check if publication probability was below 100 in first round
            if(init_p_pub < 100): # randint includes max
                # if it was lower, do a second round now with probability set to 1
                p_pub = 100
                self.gw_suc.publication_round(self, cnt_struct, p_pub, curr_time) # pass gw_coord along
                return
            else:
                # it was already set to one so this is as good as we can get
                print("__coord else__: END")
                z_utils.print_cnt_struct(cnt_struct)
                return
    """
    '''
        print publication log at GW for debugging
    '''
    """
    def print_pub_log(self, pub_log_list):
        for log in pub_log_list:
            print("__pub log__: ", log)
    """


    '''
        ongoing coordination round
    '''
    """
    def publication_round(self, gw_coord, cnt_struct, p_pub, curr_time):
        print("__pub round__: at GW ", self.id, " with p_pub: ", p_pub)
        # stop publication round if cnt_struct is already empty
        if(cnt_struct.is_empty()):
            return
            #gw_coord.coord_end_publication_round()
        
        else:
            # check for existing records of gw in cnt_struct to publish entries
            pub_records = []
            print("__pub round__: complete record_log:")
            self.print_record_log()
            pub_records = self.get_records_for_publishing(cnt_struct, curr_time)
            
            # some of GW's records were found
            if(pub_records):
                for pr in pub_records:
                    # take publication responsibility with p_pub 
                    rnd = random.randint(0,100)
                    print("__pub_round__: my rnd ", rnd, ", p_pub: ", p_pub)
                    if(rnd < p_pub):
                        #if(cnt_struct.check(pr.value)):
                        if(cnt_struct.check(pr.key)):
                            print("__pub round__: publish record ", pr)
                            # to publish: forward PubLogEntry entry to CE with value, timepoint, and sm_id for collection and further processing
                            self.ce.publish_tuple(pr, self.id)
                            # update flag in record_log to indicate that the corresponding tuple has been published (pr == PubLogEntry)
                            self.update_local_record_log(pr)
                            # remove element from bloomfilter
                            #cnt_struct.remove(pr.value) 
                            cnt_struct.remove(pr.key) 
                            print("__pub round__: updated CBF after removal at GW ", self.id)
                            z_utils.print_cnt_struct(cnt_struct)

                        # count structure is empty after publication -> not often the case
                        if(cnt_struct.is_empty()):
                            return
                            
            # checks if CBF is empty to end pub round earlier 
            if(cnt_struct.is_empty()):
                return
            
            # back at coordinator so first round is completed
            if(gw_coord == self):
                first_pub_trigger = False
                gw_coord.coord_publication_round(cnt_struct, p_pub, first_pub_trigger, curr_time)
                return
            
            # publication round not completed yet, forward remaining cnt_struct to successor
            else:
                self.gw_suc.publication_round(gw_coord, cnt_struct, p_pub, curr_time)
                return
    """     
    """
    def coord_end_publication_round(self):

        print("__END pub round:__")
        return
    """
    '''
        print counting structure at GW for debugging
    '''
    """
    def print_cnt_struct(self, cs):
        line_cnt = 0
        bit_str = ''
        for b in cs.bit_array:
            bit_str = bit_str + b.to01() + ' '
            line_cnt += 1
            if(line_cnt == 4):
                line_cnt = 0
                print(bit_str)
                bit_str = ''
        print(bit_str)
    """










