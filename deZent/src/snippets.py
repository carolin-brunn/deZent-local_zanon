  '''

            # TODO: check that there is more than 1 GW in list -> otherwise no ring can be established! -> single coordinator
            # ask every GW for its ID and succesor ID
            for tmp_gw in self.l_gws:
                # TODO: assumption: each gw_id exists only once -> same gw_id == same gw
                if (gw.id == tmp_gw.id):
                    continue
                elif(gw.id > tmp_gw.id):
                    continue
                # gw is before tmp_gw in ring
                elif (gw.id < tmp_gw.id):
                    # case tmp_gw does not have a predecessor yet -> set predecessor
                    if(tmp_gw.predecessor == None):
                        # case current gw does not have a succesor yet either -> just connect them
                        if(gw.successor == None):
                            tmp_gw.predecessor = gw
                            gw.successor = tmp_gw
                        # case potential predecessor gw already has a succesor
                        elif(gw.successor.id > tmp_gw.id):
                            tmp_suc = gw.successor
                            gw.successor = tmp_gw
                            tmp_gw.predecessor = gw
                            tmp_gw.successor = tmp_suc
                            tmp_suc.predecessor = tmp_gw

                        elif(gw.successor.id < tmp_gw.id):
                            # successor is the smallest node of the ring -> so close the ring again
                            if(gw.successor.id == min_gw_id):
                                tmp_suc = gw.successor
                                gw.successor = tmp_gw
                                tmp_gw.predecessor = gw
                                tmp_gw.successor = tmp_suc
                                tmp_suc.predecessor = tmp_gw
                            # no need to close the ring
                            #else:

                    # tmp_gw already has a predecessor -> gw needs to be inserted here  
                    elif(tmp_gw.predecessor.id < gw.id):
                        #tmp_pred = tmp_gw.predecessor
                        gw.predecessor = tmp_gw.predecessor
                        tmp_gw.predecessor.successor = gw
                        gw.successor = tmp_gw
                        tmp_gw.predecessor = gw

                    elif(tmp_gw.predecessor.id > gw.id):
                        # case new smallest ID
                        if(gw.id == min_gw_id):
                            gw.predecessor = tmp_gw.predecessor
                            tmp_gw.predecessor.successor = gw
                            gw.successor = tmp_gw
                            tmp_gw.predecessor = gw
                        elif(gw.id > min_gw_id):
                            continue
                        # TODO: no exception handling in case of negative IDs

                    if(tmp_gw.successor == None):
                        # case just two nodes so far that are put into ring now
                        if(gw.predecessor == None):
                            tmp_gw.successor = gw
                            gw.predecessor = tmp_gw
                    break
    '''

    '''
        initialize cbf with random noise to offer additional data protection
    
    def rnd_noise_to_struct(self):
        self.coord_noise = random.randint(20,30)
        self.cnt_struct.add(self.coord_noise)
    '''

    '''
    def create_cbf(self):
        cbf = 0
        self.coord_noise = random.randint(20,30) # TODO: random noise wert -> zu cnt_struct hinzufügen -> am ende deleten
        print("__create cbf__: with noise: ", self.coord_noise)
        cbf = cbf + self.coord_noise # TODO
        return cbf
    '''

    '''
        add measurement hashes to cbf to exchange data
    
    def add_measurement_to_cbf(self, cbf):
        for sm_id in self.l_sms.keys():
            for tmp_rec in self.l_sms[sm_id]["records"]:
                cbf = cbf + tmp_rec.hash # TODO: XOR with current cbf
        return cbf
    '''

    '''
    def add_measurements_to_cnt_struct(self, struct):
        for sm_id in self.l_sms.keys():
            for tmp_rec in self.l_sms[sm_id]["records"]:
                struct.add(tmp_rec)
        print("__add m__: updated gw CBF: ", struct.bit_array)
        return struct
    '''
    
    '''
        gw_coord removes noise that was added by them before data exchange
    
    def remove_initial_noise_from_cnt_struct(self, cbf):
        
        clean_cbf = cbf - self.coord_noise # TODO: delete noise from beginning with cnt_struct method
        self.cnt_struct.remove(self.coord_noise)
        print("__remove noise__: postprocessed CBF: ", self.cnt_struct.bit_array)
        #print("__remove noise__: cbf: ", cbf, ", noise: ", self.coord_noise, ", cleaned_cbf: ", clean_cbf)
        return clean_cbf
    '''
    
    """
    def request_curr_measurement_from_sm(self, curr_time):
        print("__get SM measurement__")
        # for each sm trigger current measurement and store at gw
        for sm_id in self.l_sms.keys():
            sm = self.l_sms[sm_id]["sm_instance"]
            curr_measurement = sm.measure_data()
            new_record = Record(curr_measurement, curr_time)
            self.l_sms[sm_id]["records"].append(new_record) 
    """
    
    """
    def add_m_to_record_log(self, curr_measurement, sm_id, curr_time):
        # measurement was already observed before -> add (sm: t) or update t for this observation
        if(curr_measurement in self.record_log):
            #self.record_log[curr_measurement][sm_id] = curr_time
            self.record_log[curr_measurement][sm_id] = curr_time

        # measurement value has never been seen before -> add to dictionary
        else:
            self.record_log[curr_measurement] = {sm_id: curr_time}
    """

    """
    def apply_deltat_to_records(self, curr_time):
        #print("__remove outdated measurements__")
        delta_t = self.zanon.delta_t
        t_limit = curr_time - delta_t
        #print("curr_time: ", curr_time, " dt: ", delta_t, " limit: ", t_limit)
        cut_idx = 0

        # check recordlist of each smart meter connected with gateway
        for key in self.l_sms.keys():
            record_list = self.l_sms[key]["records"] 

            # nothing to delete if list is already empty
            if(len(record_list) == 0):
                break
            
            for tmp_idx in range(len(record_list)):
                tmp_record = record_list[tmp_idx]

                # find entries whose timepoints are too old
                if(tmp_record.timepoint < t_limit):
                    cut_idx = tmp_idx+1

                # list is ordered, once a time_point is within delta_t all the following entries will be as well
                else:
                    break

            # cut list at indicated index
            updated_record_list = record_list[cut_idx:]
            self.l_sms[key]["records"] = updated_record_list
    """
            