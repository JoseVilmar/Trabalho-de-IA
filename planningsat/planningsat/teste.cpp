/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   main.cpp
 * Author: alexandre
 *
 * Created on 10 de Abril de 2018, 22:51
 */

#include <algorithm>
#include <iostream>
#include <cstdlib>
#include <vector>
#include <queue>
#include <cmath>
#include <climits>
#include <stack>
#include <string>
#include <map>
#include <set>
#include <iterator>
#include <memory>
#include <stdexcept>
#include <array>
#include <sstream>
#include <iostream>
#include <fstream>
#include <ctime>

using namespace std;

/*
 * 
 */
vector<string> actions;
map<string, vector<string> > preconditions;
map<string, vector<string> > effects;
set<string> propositions;
vector<string> propositionsVector;
vector<string> initialState;
vector<string> finalState;

//MAPPING STRUCTURES
map<string, int> mappingToInt;
vector<string> mappingToString(1,"");
int numberMapping=0;

//output Matrix
vector<vector<int> > outputMatrix;
vector<int> finalStateNumbers;

void split(const string& s, char delim,vector<string>& v) {
    auto i = 0;
    auto pos = s.find(delim);
    if (pos == string::npos){
         v.push_back(s.substr(i, s.length()));
         return;
    }
    while (pos != string::npos) {
      v.push_back(s.substr(i, pos-i));
      i = ++pos;
      pos = s.find(delim, pos);

      if (pos == string::npos)
         v.push_back(s.substr(i, s.length()));
    }
}    

string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(popen(cmd, "r"), pclose);
    if (!pipe) throw std::runtime_error("popen() failed!");
    while (!feof(pipe.get())) {
        if (fgets(buffer.data(), 128, pipe.get()) != nullptr)
            result += buffer.data();
    }
    return result;
}

int isNegated(string input){
    return (input[0] == '~') ? 1 : 0;
}
int isMapped(string input){
    return (mappingToInt.find(input) != mappingToInt.end()) ? 1 : 0;
}

void addToMapping(string input){      
    if(!isMapped(input)){
        mappingToInt[input] = ++numberMapping;  
        mappingToString.push_back(input);
        
    }
}

int getMappingToInt(string input){
    if(isNegated(input))
        return -1*mappingToInt[input.substr(1,input.size()-1)];
    return mappingToInt[input];
}

string getPositiveLiteral(string input){
    return (isNegated(input)) ? input.substr(1,input.size()-1) : input;
}

void loadData(){
    string inputAction, inputPrecondition, inputEffect;
    string inputObjective, inputGoal;
    getline(cin,inputAction);
    while(inputAction.size()!=0){
        actions.push_back(inputAction);
        getline(cin,inputPrecondition);
        getline(cin,inputEffect);

        vector<string> tokenizedPreconditions, tokenizedEffects;
        split(inputPrecondition,';', tokenizedPreconditions);
        split(inputEffect,';', tokenizedEffects);

        preconditions[inputAction] = tokenizedPreconditions;
        effects[inputAction] = tokenizedEffects;

        for (string elem : tokenizedPreconditions)
            propositions.insert(getPositiveLiteral(elem));

        for (string elem : tokenizedEffects)
            propositions.insert(getPositiveLiteral(elem));


        getline(cin,inputAction);
    }
    getline(cin,inputObjective);
    getline(cin,inputGoal);

    split(inputObjective,';', initialState);    
    split(inputGoal,';', finalState);
    for (string elem : initialState)
        propositions.insert(getPositiveLiteral(elem));
    for (string elem : finalState)
        propositions.insert(getPositiveLiteral(elem));    
        
    std::copy(propositions.begin(), propositions.end(), std::back_inserter(propositionsVector));    

}

void addingNewPropositionsWithLevel(int level){
    for (auto elem : propositions) {
        string proposition = to_string(level) + "_" + getPositiveLiteral(elem);
        addToMapping(proposition);
    }
}

void addingConstraintInitialStateWithLevel(){
    set<string> allEnvolvedPropositions;
    set<string> notEnvolvedPropositions;
    for (string elem : initialState) {
        allEnvolvedPropositions.insert(elem);        
        string initialPropositionString = to_string(1) + "_" + elem;
        int polarity = mappingToInt[initialPropositionString];
        vector<int> unitaryProposition = {polarity};
        outputMatrix.push_back(unitaryProposition);
    }
    set_difference(propositions.begin(), propositions.end(), allEnvolvedPropositions.begin(), allEnvolvedPropositions.end(), inserter(notEnvolvedPropositions, notEnvolvedPropositions.end()));
    for (string elem : notEnvolvedPropositions) {
        string initialPropositionString = to_string(1) + "_" + elem;
        int polarity = -1*mappingToInt[initialPropositionString];
        vector<int> unitaryProposition = {polarity};
        outputMatrix.push_back(unitaryProposition);
    }
}
void addingConstraintFinalStateWithLevel(int level){
	finalStateNumbers.clear();
    for (string elem : finalState) {     
        string finalPropositionString = to_string(level) + "_" + elem;
        int polarity = mappingToInt[finalPropositionString];
        finalStateNumbers.push_back(polarity);
        //vector<int> unitaryProposition = {polarity};
        //outputMatrix.push_back(unitaryProposition);
    }
}
void addingInitialStateToMapping(){
    for (string state : initialState) {
        addToMapping(to_string(1) + "_" + getPositiveLiteral(state));
    }
}
void addingFinalStateToMapping(int level){
    for (string state : finalState) {
        addToMapping(to_string(level) + "_" + getPositiveLiteral(state));
    }
}

void addingNewActionsToMappingWithLevel(int level){
    for (string elem : actions) {
        string action = to_string(level) + "_" + elem;
        addToMapping(action);
    }
}

void addingConstraintActionsWithLevel(int level){
    for (int i = 0; i < actions.size(); i++) {           
        for (int j = i+1; j < actions.size(); j++) {
            string action_1 = to_string(level) + "_"  + actions[i];
            string action_2 = to_string(level) + "_"  + actions[j];

            int u = -1*mappingToInt[action_1];
            int v = -1*mappingToInt[action_2];
            vector<int> newConstraint = {u,v};
            outputMatrix.push_back(newConstraint);                   
        }
    }   
    vector<int> allConstraintActions;
    for (int i = 0; i < actions.size(); i++) {
        string actionString = to_string(level) + "_"  + actions[i];
        int mappedAction = mappingToInt[actionString];
        allConstraintActions.push_back(mappedAction);
    }
    outputMatrix.push_back(allConstraintActions);
}

void addingConstraintActionPreconditionWithLevel(int level){
    for (string action : actions) {
        string actionString = to_string(level) + "_" + action;
        int actionMapped = -1*mappingToInt[actionString];
        for (string precondition : preconditions[action]) {
            string preconditionString = to_string(level) + "_" + getPositiveLiteral(precondition);
            int preconditionMapped = (isNegated(precondition)) ? -1*mappingToInt[preconditionString] : mappingToInt[preconditionString];
            vector<int> constraint = {actionMapped, preconditionMapped};
            outputMatrix.push_back(constraint);                
        }
    }
}

void addingConstraintActionEffectsWithLevel(int level){
    for (string action : actions) {
        string actionString = to_string(level) + "_" + action;
        int actionMapped = -1*mappingToInt[actionString];
        for (string effect : effects[action]) {
            string effectString = to_string(level+1) + "_" + getPositiveLiteral(effect);
            int effectMapped = (isNegated(effect)) ? -1*mappingToInt[effectString] : mappingToInt[effectString];
            vector<int> constraint = {actionMapped, effectMapped};
            outputMatrix.push_back(constraint);                
        }            
    }
}    

void addingConstraintActionPosEffectsWithLevel(int level){
    for (string action : actions) {
        string actionString = to_string(level) + "_" + action;
        int actionMapped = mappingToInt[actionString];
        set<string> allEnvolvedPropositions;
        set<string> notEnvolvedPropositions;
        for (string precondition : preconditions[action]) {
            allEnvolvedPropositions.insert(getPositiveLiteral(precondition));
        }            
        for (string effect : effects[action]) {
            allEnvolvedPropositions.insert(getPositiveLiteral(effect));
        }
        set_difference(propositions.begin(), propositions.end(), allEnvolvedPropositions.begin(), allEnvolvedPropositions.end(), inserter(notEnvolvedPropositions, notEnvolvedPropositions.end()));
        for (string elem : notEnvolvedPropositions) {
            string precond = to_string(level) + "_" + elem;
            string poscond = to_string(level+1) + "_" + elem;

            int precondNumber = mappingToInt[precond];
            int poscondNumber = mappingToInt[poscond];

            vector<int> constraint_1 = {-1*actionMapped, precondNumber, -1*poscondNumber};
            vector<int> constraint_2 = {-1*actionMapped, -1*precondNumber, poscondNumber};
            outputMatrix.push_back(constraint_1);
            outputMatrix.push_back(constraint_2);               
        }
    }        
}
void addingConstraintOtimization(int level){	
	for(int i =0; i < propositionsVector.size(); i++){
		if(propositionsVector[i].substr(0,3) == "on_" || propositionsVector[i].substr(0,8) == "holding_")
		for(int j=i+1; j < propositionsVector.size(); j++){
			if(propositionsVector[i].substr(0,5) == propositionsVector[j].substr(0,5)){
				string on_1 = to_string(level) + "_" + propositionsVector[i];
				string on_2 = to_string(level) + "_" + propositionsVector[j];
				
				int on_1_int = mappingToInt[on_1];
			    int on_2_int = mappingToInt[on_2];
			    
			    vector<int> condition = {-1*on_1_int, -1*on_2_int};
			    outputMatrix.push_back(condition);
			}
		} 
	}/* 
	for (int i =0; i < actions.size(); i++) {
        if(actions[i].substr(0,8) == "pick-up_")
        for(int j=0; j < actions.size(); j++){
				if(actions[j].substr(0,8) == "unstack_"){
					string action_1 = to_string(level) + "_" + actions[i];
					string action_2 = to_string(level+1) + "_" + actions[j];
					addToMapping(action_2);
					int action_1_int = mappingToInt[action_1];
					int action_2_int = mappingToInt[action_2];
					vector<int> condition = {-1*action_1_int, -1*action_2_int};
			        outputMatrix.push_back(condition);
				}
		}
	}
	for (int i =0; i < actions.size(); i++) {
        if(actions[i].substr(0,8) == "unstack_")
        for(int j=i+1; j < actions.size(); j++){
				if(actions[j].substr(0,8) == "unstack_"){
					string action_1 = to_string(level) + "_" + actions[i];
					string action_2 = to_string(level+1) + "_" + actions[j];
					addToMapping(action_2);
					int action_1_int = mappingToInt[action_1];
					int action_2_int = mappingToInt[action_2];
					vector<int> condition = {-1*action_1_int, -1*action_2_int};
			        outputMatrix.push_back(condition);
				}
		}
	}	
	for (int i =0; i < actions.size(); i++) {
        if(actions[i].substr(0,6) == "stack_")
        for(int j=i+1; j < actions.size(); j++){
				if(actions[j].substr(0,6) == "stack_"){
					string action_1 = to_string(level) + "_" + actions[i];
					string action_2 = to_string(level+1) + "_" + actions[j];
					addToMapping(action_2);
					int action_1_int = mappingToInt[action_1];
					int action_2_int = mappingToInt[action_2];
					vector<int> condition = {-1*action_1_int, -1*action_2_int};
			        outputMatrix.push_back(condition);
				}
		}
	}	
	for (int i =0; i < actions.size(); i++) {
        if(actions[i].substr(0,8) == "pick-up_")
        for(int j=i+1; j < actions.size(); j++){
				if(actions[j].substr(0,8) == "pick-up_"){
					string action_1 = to_string(level) + "_" + actions[i];
					string action_2 = to_string(level+1) + "_" + actions[j];
					addToMapping(action_2);
					int action_1_int = mappingToInt[action_1];
					int action_2_int = mappingToInt[action_2];
					vector<int> condition = {-1*action_1_int, -1*action_2_int};
			        outputMatrix.push_back(condition);
				}
		}
	}	*/

}


void outputFileCNF(vector<vector<int> > outputMatrix, int &currentMatrixLine, vector<int> finalState, string tmpFile, string fileName){
    ofstream outputFile;
    fstream inputFile;
    inputFile.open(tmpFile, std::ios_base::app);
	currentMatrixLine;
    for (int i = currentMatrixLine; i < outputMatrix.size(); i++) {
        for (int j = 0; j < outputMatrix[i].size(); j++) {
            inputFile << outputMatrix[i][j] << " ";
        }
        inputFile << 0 << endl;    
    }
    currentMatrixLine = outputMatrix.size();
	inputFile.close();
	inputFile.open(tmpFile, std::ios_base::in);
    outputFile.open(fileName);
    outputFile << "p cnf " << numberMapping << " " << outputMatrix.size() + finalStateNumbers.size() << endl;    
	outputFile << inputFile.rdbuf();
    for(int i=0; i < finalState.size(); i++){
		outputFile << finalState[i] <<  " " << 0 << endl;
	}
    inputFile.close();
    outputFile.close();    
}

void executeZCHAFF(vector<int> &instance, string fileName){
       
    string input = string("./glucose_static -model") + " " + fileName;
    string result = exec(input.c_str());

    string prefix("s SATISFIABLE");

    istringstream iss(result);
    stringstream ss;

    string line;
    string token;
    while (getline(iss, line))
    {
            if (!line.compare(0, prefix.size(), prefix)){
                    getline(iss, line);
                    ss << line;
                    ss >> token;
                    instance.push_back(0);
                    for(int i =0; i < numberMapping; i++){
                            int variable;
                            ss >> variable;
                            instance.push_back(variable);					
                    }			
                    break;	
            }				
    }
}


    
int main(int argc, char** argv) {
    clock_t start, end;
    start = clock();

    loadData();
    int level = 1;
    int currentMatrixLine = 0;

    vector<int> sat_output;
    string fileName = "planning.cnf";
    string tmpFile = "tmp.cnf";
    
    addingInitialStateToMapping();
    addingNewPropositionsWithLevel(1);
    addingConstraintInitialStateWithLevel();
   // addingConstraintOtimization(1);
    
    ofstream output;
    output.open(tmpFile);
    output.close();
    while(level < 100){
		cout << "construindo level: " << level << endl;
		addingNewActionsToMappingWithLevel(level); 
		addingNewPropositionsWithLevel(level+1);	
		addingConstraintActionsWithLevel(level); 
		addingConstraintActionPreconditionWithLevel(level); 
		addingConstraintActionEffectsWithLevel(level);
		addingConstraintActionPosEffectsWithLevel(level);
		addingConstraintOtimization(level);
		addingConstraintFinalStateWithLevel(level+1);
		level++;
	}
    
    while(sat_output.empty()){
		cout << "construindo level: " << level << endl;
		addingNewActionsToMappingWithLevel(level); 
		addingNewPropositionsWithLevel(level+1);	
		addingConstraintActionsWithLevel(level); 
		addingConstraintActionPreconditionWithLevel(level); 
		addingConstraintActionEffectsWithLevel(level);
		addingConstraintActionPosEffectsWithLevel(level);
		addingConstraintOtimization(level);
		addingConstraintFinalStateWithLevel(level+1);
	    //addingConstraintOtimization(level+1);
		
		outputFileCNF(outputMatrix, currentMatrixLine, finalStateNumbers, tmpFile ,fileName);
		cout << "avaliando level: " << level << endl;		    
		executeZCHAFF(sat_output,fileName);	
		
		//if(sat_output.empty()){
		//	for (int i = 0; i < finalState.size(); i++)
		//		outputMatrix.pop_back();
			
	//	}		
		level++;
		
	}
	
    if(!sat_output.empty()){
        for (int i = 1; i <= level; i++) {
            for (string elem : actions) {
                if(sat_output[mappingToInt[to_string(i) + "_" + elem]] > 0)
                    cout << to_string(i) + "_" + elem << endl;                
            }
        }

    }
    end = clock();
    cout << "TIME(SEC) " << static_cast<double>(end-start) / CLOCKS_PER_SEC << endl;            
    return 0;
}
