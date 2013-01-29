'''
Created on Mar 13, 2012

@author: jhkwakkel
'''
from __future__ import division
import copy

import numpy as np
import matplotlib.pyplot as plt

from expWorkbench.uncertainties import CategoricalUncertainty, ParameterUncertainty
from expWorkbench import EMAlogging, vensim, save_results, load_results
from expWorkbench.vensim import VensimModelStructureInterface, VensimError
from expWorkbench.outcomes import Outcome
from expWorkbench.ema_exceptions import CaseError 
from expWorkbench import ModelEnsemble

from analysis import prim

class EnergyTrans(VensimModelStructureInterface):
    modelFile = r'\CESUN_optimized_new.vpm'
    
    #outcomes    
    outcomes = [Outcome('total fraction new technologies' , time=True),  
                Outcome('total capacity installed' , time=True),  
                Outcome("monitor for Trigger subsidy T2", time=True),
                Outcome("monitor for Trigger subsidy T3", time=True), 
                Outcome("monitor for Trigger subsidy T4", time=True),
                Outcome("monitor for Trigger addnewcom", time=True)]
    
    activation = [Outcome("monitor for Trigger subsidy T2", time=True),
                  Outcome("monitor for Trigger subsidy T3", time=True), 
                  Outcome("monitor for Trigger subsidy T4", time=True),
                  Outcome("monitor for Trigger addnewcom", time=True)]

    uncertainties = [ParameterUncertainty((14000,16000), "ini cap T1"),
                     ParameterUncertainty((1,2), "ini cap T2"),
                     ParameterUncertainty((1,2), "ini cap T3"),
                     ParameterUncertainty((1,2), "ini cap T4"),
                     ParameterUncertainty((500000,1500000), "ini cost T1"), #1000000
                     ParameterUncertainty((5000000,10000000), "ini cost T2"), #8000000
                     ParameterUncertainty((5000000,10000000), "ini cost T3"), #8000000
                     ParameterUncertainty((5000000,10000000), "ini cost T4"), #8000000
                     ParameterUncertainty((5000000,10000000), "ini cum decom cap T1"), 
                     ParameterUncertainty((1,100), "ini cum decom cap T2"), 
                     ParameterUncertainty((1,100), "ini cum decom cap T3"), 
                     ParameterUncertainty((1,100), "ini cum decom cap T4"), 
                     ParameterUncertainty((1,5), "average planning and construction period T1"), 
                     ParameterUncertainty((1,5), "average planning and construction period T2"), 
                     ParameterUncertainty((1,5), "average planning and construction period T3"), 
                     ParameterUncertainty((1,5), "average planning and construction period T4"), 
                     ParameterUncertainty((0.85,0.95), "ini PR T1"),
                     ParameterUncertainty((0.7,0.95), "ini PR T2"),
                     ParameterUncertainty((0.7,0.95), "ini PR T3"), 
                     ParameterUncertainty((0.7,0.95), "ini PR T4"), 

                     ParameterUncertainty((30,50), "lifetime T1"),
                     ParameterUncertainty((15,20), "lifetime T2"),
                     ParameterUncertainty((15,20), "lifetime T3"),
                     ParameterUncertainty((15,20), "lifetime T4"),      

                     #One uncertain development over time -- smoothed afterwards
                     ParameterUncertainty((0.03,0.035), "ec gr t1"), #0.03                        
                     ParameterUncertainty((-0.01,0.03), "ec gr t2"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t3"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t4"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t5"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t6"), #0.03                        
                     ParameterUncertainty((-0.01,0.03), "ec gr t7"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t8"), #0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t9"),#0.03
                     ParameterUncertainty((-0.01,0.03), "ec gr t10"), #0.03                
                    
                     #Uncertainties in Random Functions
                     ParameterUncertainty((0.9,1), "random PR min"),        
                     ParameterUncertainty((1,1.1), "random PR max"),
                     ParameterUncertainty((1,100), "seed PR T1", integer=True), 
                     ParameterUncertainty((1,100), "seed PR T2", integer=True),
                     ParameterUncertainty((1,100), "seed PR T3", integer=True),
                     ParameterUncertainty((1,100), "seed PR T4", integer=True),
            
                     #Uncertainties in Preference Functions
                     ParameterUncertainty((2,5), "absolute preference for MIC"),
                     ParameterUncertainty((1,3), "absolute preference for expected cost per MWe"),
                     ParameterUncertainty((2,5), "absolute preference against unknown"),  
                     ParameterUncertainty((1,3), "absolute preference for expected progress"),
                     ParameterUncertainty((2,5), "absolute preference against specific CO2 emissions"),  
                     
                     #Uncertainties DIE NOG AANGEPAST MOETEN WORDEN
                     ParameterUncertainty((1,2), "performance expected cost per MWe T1"),
                     ParameterUncertainty((1,5), "performance expected cost per MWe T2"),
                     ParameterUncertainty((1,5), "performance expected cost per MWe T3"),
                     ParameterUncertainty((1,5), "performance expected cost per MWe T4"),
                     ParameterUncertainty((4,5), "performance CO2 avoidance T1"),
                     ParameterUncertainty((1,5), "performance CO2 avoidance T2"),
                     ParameterUncertainty((1,5), "performance CO2 avoidance T3"),
                     ParameterUncertainty((1,5), "performance CO2 avoidance T4"),
                    
                     #Switches op technologies
                     CategoricalUncertainty((0,1), "SWITCH T3", default = 1),
                     CategoricalUncertainty((0,1), "SWITCH T4", default = 1),

                     CategoricalUncertainty([(0, 0, 0, 0, 1),
                                             (0, 0, 0, 1, 0),
                                             (0, 0, 0, 1, 1),
                                             (0, 0, 1, 0, 0),
                                             (0, 0, 1, 0, 1),
                                             (0, 0, 1, 1, 0),
                                             (0, 0, 1, 1, 1),
                                             (0, 1, 0, 0, 0),
                                             (0, 1, 0, 0, 1),
                                             (0, 1, 0, 1, 0),
                                             (0, 1, 0, 1, 1),
                                             (0, 1, 1, 0, 0),
                                             (0, 1, 1, 0, 1),
                                             (0, 1, 1, 1, 0),
                                             (0, 1, 1, 1, 1),
                                             (1, 0, 0, 0, 0),
                                             (1, 0, 0, 0, 1),
                                             (1, 0, 0, 1, 0),
                                             (1, 0, 0, 1, 1),
                                             (1, 0, 1, 0, 0),
                                             (1, 0, 1, 0, 1),
                                             (1, 0, 1, 1, 0),
                                             (1, 0, 1, 1, 1),
                                             (1, 1, 0, 0, 0),
                                             (1, 1, 0, 0, 1),
                                             (1, 1, 0, 1, 0),
                                             (1, 1, 0, 1, 1),
                                             (1, 1, 1, 0, 0),
                                             (1, 1, 1, 0, 1),
                                             (1, 1, 1, 1, 0),
                                             (1, 1, 1, 1, 1)], 
                                            "preference switches"),
                     ]
       
       
    def model_init(self, policy, kwargs):
        super(EnergyTrans, self).model_init(policy, kwargs)

        #pop name
        policy = copy.copy(policy)
        policy.pop('name')
        
        for key, value in policy.items():
            vensim.set_value(key, value)

    def run_model(self, case):
        switches = case.pop("preference switches")

        case["SWITCH preference for MIC"] = switches[0]
        case["SWITCH preference for expected cost per MWe"]= switches[1]
        case["SWITCH preference against unknown"]= switches[2]
        case["SWITCH preference for expected progress"]= switches[3]
        case["SWITCH preference against specific CO2 emissions"]= switches[4]
            
        for key, value in case.items():
            vensim.set_value(key, value)
        EMAlogging.debug("model parameters set successfully")
        
        EMAlogging.debug("run simulation, results stored in " + self.workingDirectory+self.resultFile)
        try:
            vensim.run_simulation(self.workingDirectory+self.resultFile)
        except VensimError:
            raise

        results = {}
        error = False
        for output in self.outcomes:
            EMAlogging.debug("getting data for %s" %output.name)
            result = vensim.get_data(self.workingDirectory+self.resultFile, 
                              output.name 
                              )
            EMAlogging.debug("successfully retrieved data for %s" %output.name)
            if not result == []:
                if result.shape[0] != self.runLength:
                    a = np.zeros((self.runLength))
                    a[0:result.shape[0]] = result
                    result = a
                    error = True
            
            else:
                result = result[0::self.step]
            try:
                results[output.name] = result
            except ValueError:
                print "what"

        for output in self.activation:
            value = results[output.name]
            time = results["TIME"]
            activationTimeStep = time[value>0]
            if activationTimeStep.shape[0] > 0:
                activationTimeStep = activationTimeStep[0]
            else:
                activationTimeStep = np.array([0])
            results[output.name] = activationTimeStep
            
        
        self.output = results   
        if error:
            raise CaseError("run not completed", case) 



def classify(data):
    
    result = data['total fraction new technologies']    
    classes =  np.zeros(result.shape[0])
    classes[result[:, -1] < 0.6] = 1
    
    return classes

if __name__ == "__main__":
    EMAlogging.log_to_stderr(EMAlogging.INFO)
    model = EnergyTrans(r"..\..\models\EnergyTrans", "ESDMAElecTrans")
       
    ensemble = ModelEnsemble()
    ensemble.set_model_structure(model)
    ensemble.parallel = True
    
    results = ensemble.perform_experiments(1000)
    
    results = load_results(r'prim data 100 cases.cPickle')
    boxes = prim.perform_prim(results, 
                      classify=classify,
                      mass_min=0.05, 
                      threshold=0.8)
    prim.write_prim_to_stdout(boxes, filter=True)
    prim.show_boxes_together(boxes, results)
    
    plt.show()