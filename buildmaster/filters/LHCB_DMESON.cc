#include "LHCB_DMESON.h"

void LHCB_DMESON_R_13_5Filter::ReadData()
{
    // Opening files
    fstream rData, rCorr;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/5TeV_ratios.dat";
    rData.open(DataFile.str().c_str(), ios::in);

    if (rData.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Correlation matrix
    stringstream DataFileCorr("");
    DataFileCorr << dataPath() << "rawdata/" << fSetName 
	       << "/corr_tot.dat";
    rCorr.open(DataFileCorr.str().c_str(), ios::in);

    if (rCorr.fail()) {
        cerr << "Error opening data file " << DataFileCorr.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    std::vector<double> totsys(fNData);        
    double pt, statup, statdown, sysup, sysdown;
    double stat, sys, delta_stat, delta_sys;

    for (int i = 0; i < fNData; i++)
    {
        getline(rData,line);                  
        istringstream lstream(line); 

        lstream >> pt;
        fKin1[i] = pt;          
        fKin2[i] = 1;         //dummy value    
        fKin3[i] = 1;         //dummy value      

        lstream >> fData[i];        
                 
        lstream >> statup >> statdown;
        symmetriseErrors(statup, statdown, &stat, &delta_stat);
        fData[i] += delta_stat;
        fStat[i] = stat;

        lstream >> sysup >> sysdown;
        symmetriseErrors(sysup, sysdown, &sys, &delta_sys);
        fData[i] += delta_sys;
        totsys[i] = sys;

        fSys[i][0].add  = sys;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";
    }
}


void LHCB_DMESON_N7Filter::ReadData()
{
    // Opening files
    fstream rData, rCorr;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/7TeV_ratios.dat";
    rData.open(DataFile.str().c_str(), ios::in);

    if (rData.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    std::vector<double> totsys(fNData);        
    double pT, statup, statdown, sysup, sysdown;
    double stat, sys, delta_stat, delta_sys;

    for (int i = 0; i < fNData; i++)
    {
        getline(rData,line);                  
        istringstream lstream(line); 
        
        lstream >> pT;
        fKin1[i] = pT;          
        fKin2[i] = 1;         //dummy value    
        fKin3[i] = 1;         //dummy value      

        lstream >> fData[i];

        lstream >> statup >> statdown;
        symmetriseErrors(statup, statdown, &stat, &delta_stat);
        fData[i] += delta_stat;
        fStat[i] = stat;

        lstream >> sysup >> sysdown;
        symmetriseErrors(sysup, sysdown, &sys, &delta_sys);
        fData[i] += delta_sys;
        totsys[i] = sys;   

        fSys[i][0].add  = sys;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";
    }   
}

void LHCB_DMESON_N5Filter::ReadData()
{
    // Opening files
    fstream rData, rCorr;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/5TeV_ratios.dat";
    rData.open(DataFile.str().c_str(), ios::in);

    if (rData.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    std::vector<double> totsys(fNData);        
    double pT, statup, statdown, sysup, sysdown;
    double stat, sys, delta_stat, delta_sys;

    for (int i = 0; i < fNData; i++)
    {
        getline(rData,line);                  
        istringstream lstream(line); 
        
        lstream >> pT;
        fKin1[i] = pT;          
        fKin2[i] = 1;         //dummy value    
        fKin3[i] = 1;         //dummy value      

        lstream >> fData[i];

        lstream >> statup >> statdown;
        symmetriseErrors(statup, statdown, &stat, &delta_stat);
        fData[i] += delta_stat;
        fStat[i] = stat;

        lstream >> sysup >> sysdown;
        symmetriseErrors(sysup, sysdown, &sys, &delta_sys);
        fData[i] += delta_sys;
        totsys[i] = sys;   

        fSys[i][0].add  = sys;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";
    }
}

void LHCB_DMESON_N13Filter::ReadData()
{
    // Opening files
    fstream rData, rCorr;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/13TeV_ratios.dat";
    rData.open(DataFile.str().c_str(), ios::in);

    if (rData.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    std::vector<double> totsys(fNData);        
    double pT, statup, statdown, sysup, sysdown;
    double stat, sys, delta_stat, delta_sys;

    for (int i = 0; i < fNData; i++)
    {
        getline(rData,line);                  
        istringstream lstream(line); 
        
        lstream >> pT;
        fKin1[i] = pT;          
        fKin2[i] = 1;         //dummy value    
        fKin3[i] = 1;         //dummy value      

        lstream >> fData[i];

        lstream >> statup >> statdown;
        symmetriseErrors(statup, statdown, &stat, &delta_stat);
        fData[i] += delta_stat;
        fStat[i] = stat;

        lstream >> sysup >> sysdown;
        symmetriseErrors(sysup, sysdown, &sys, &delta_sys);
        fData[i] += delta_sys;
        totsys[i] = sys;        
                 
        fSys[i][0].add  = sys;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";
    }
}

void LHCB_DMESON_R_nuclear_forwardFilter::ReadData()
{
    // Opening files
    fstream rRatio;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/data_Fwd.csv";
    rRatio.open(DataFile.str().c_str(), ios::in);

    if (rRatio.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    double ratio, sys_uncorr, sys_corr, y, pT;
    double mc = 1.51;

    for (int i = 0; i < fNData; i++)
    {
        getline(rRatio,line);                  
        istringstream lstream(line); 

        lstream >> pT >> y;

        fKin1[i] = y;         //rapidity
        fKin2[i] = pow(pT,2) + pow(mc,2);    // pT^2 + mc^2    
        fKin3[i] = 5000;         // \sqrt(s) GeV      

        lstream >> ratio >> sys_uncorr >> sys_corr;
        fData[i] = ratio;
        fStat[i] = 0.;

        fSys[i][0].add  = sys_uncorr;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";

        fSys[i][1].add  = sys_corr;
        fSys[i][1].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][1].type = ADD;  
        fSys[i][1].name = "CORR";
    }
}


void LHCB_DMESON_R_nuclear_backwardFilter::ReadData()
{
    // Opening files
    fstream rRatio;

    // Data
    stringstream DataFile("");
    DataFile << dataPath() << "rawdata/" << fSetName 
	    << "/data_Bwd.csv";
    rRatio.open(DataFile.str().c_str(), ios::in);

    if (rRatio.fail()) {
        cerr << "Error opening data file " << DataFile.str() << endl;
        exit(-1);
    }

    // Starting filter
    string line;
    double ratio, sys_uncorr, sys_corr, y, pT;
    double mc = 1.51;

    for (int i = 0; i < fNData; i++)
    {
        getline(rRatio,line);                  
        istringstream lstream(line); 

        lstream >> pT >> y;

        fKin1[i] = y;         //rapidity
        fKin2[i] = pow(pT,2) + pow(mc,2);    // pT^2 + mc^2    
        fKin3[i] = 5000;         // \sqrt(s) GeV      

        lstream >> ratio >> sys_uncorr >> sys_corr;
        fData[i] = ratio;
        fStat[i] = 0.;


        fSys[i][0].add  = sys_uncorr;
        fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][0].type = ADD;  
        fSys[i][0].name = "UNCORR";

        fSys[i][1].add  = sys_corr;
        fSys[i][1].mult = fSys[i][0].add/fData[i]*1e2;
        fSys[i][1].type = ADD;  
        fSys[i][1].name = "CORR";
    }
}
