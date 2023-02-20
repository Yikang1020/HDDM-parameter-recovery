# This script contains some frequently used function.


# generate random perfomance 
def gen_performance(n_subjs=12, n_trials=50, effect=0, n_cond = 1):

    # generate params at population level
    params = hddm.generate.gen_rand_params()
    params['v_slope'] = effect
    params['v_inter'] = 1
    params['sv'] = 0
    params['z'] = 0.7
    del params['v']
    reg_outcomes=['v']
    share_noise = ('a','v','t','st','sz','sv','z', 'v_slope', 'v_inter')
    group_params=[]

    # set valid param ranges
    bounds = {'a': (0, np.inf),
              'z': (0, 1),
              't': (0, np.inf), 
              'st': (0, np.inf),
              'sv': (0, np.inf),
              'sz': (0, 1)
    }


    for i_subj in range(n_subjs):
        # generate params at subject level
        subj_params = kabuki.generate._add_noise({'none': params}, 
                                   noise=OrderedDict([('v', 0.2),
                                   ('a', 0.2),
                                   ('t', 0.1),
                                   ('sv', 0.1),
                                    ('z',0.1),
                                   ('v_inter', 0.1)]), 
                                   share_noise=share_noise,
                                            check_valid_func=hddm.utils.check_params_valid,
                                            bounds=bounds,
                                            exclude_params={'reg_outcomes', 'st', 'sv', 'sz'})['none']

        #generate v
        wfpt_params = deepcopy(subj_params)
        wfpt_params.pop('v_inter')
        effect = wfpt_params.pop('v_slope')
        x1 = np.random.randint(2,size=n_trials)
        x1 = np.arange(n_cond)
        wfpt_params['v'] = (effect*x1) + subj_params['v_inter']

        #generate rt and choice of each trial
        i_params = deepcopy(wfpt_params)
        sampled_rts = pd.DataFrame(np.zeros((n_trials, 2)), columns=['rt', 'response'])
        for i_sample in x1:
            #get current params
            for p in reg_outcomes:
                i_params[p] = wfpt_params[p][i_sample]
            #sample
            sampled_rts.iloc[(0+int(n_trials/n_cond)*i_sample):(int(n_trials/n_cond)+int(n_trials/n_cond)*i_sample),:] = hddm.generate.gen_rts(size=int(n_trials/n_cond), method='drift', dt=1e-3, **i_params).values
        sampled_rts['subj_idx']=i_subj
        sampled_rts['cov']=np.ones(int(n_trials))
        subj_data=sampled_rts

        # create dataframe
        subj_params = pd.DataFrame([subj_params])
        # add subject
        subj_params['subj_idx'] = i_subj
        subj_params['v']=wfpt_params['v'].mean()


        # param v
        subj_v = pd.DataFrame({'v':wfpt_params['v'],
                 'cov':x1,
                'subj_idx':i_subj})


        #concatante subj_data to group_data
        if i_subj == 0:
            group_params = subj_params
        else:
            group_params = pd.concat((group_params, subj_params), ignore_index=True)

        #concatante subj_data to group_data
        if i_subj == 0:
            data = subj_data
        else:
            data = pd.concat((data, subj_data), ignore_index=True)

        #concatante subj_data to group_data
        if i_subj == 0:
            wfpt_v = subj_v
        else:
            wfpt_v = pd.concat((wfpt_v, subj_v), ignore_index=True)
    
    return