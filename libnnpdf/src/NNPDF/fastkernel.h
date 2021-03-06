// $Id$
//
// NNPDF++ 2012
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it
//          Luigi Del Debbio, luigi.del.debbio@ed.ac.uk

// libnnpdf 2014 nph

#pragma once

#include <string>
#include <vector>
#include <istream>
#include <fstream>
#include <sstream>

#include <map>

#include "common.h"

namespace NNPDF
{

    // Helper for gcc
    template <typename T>
    std::string ToString(T val)
    {
        std::stringstream stream;
        stream << val;
        return stream.str();
    }

   /**
    * \class FKHeader
    * \brief Class for parsing the header of FK tables
    */
    class FKHeader
    {
    public:
        FKHeader();   //!< Prototype constructor
        FKHeader(std::istream&);                  //!< Construct from istream
        FKHeader(std::string const& filename);   //!< Construct from file
        FKHeader(FKHeader const&);               //!< Copy-construct
        ~FKHeader();                             //!< Destructor

        void Read(std::istream&);           //!< Read FKTable header from ostream
        void Print(std::ostream&) const;    //!< Print FKTable header to ostream
        void ResetFlavourMap();             //!< Resets the flavourmap to the maximal version

        typedef std::map<std::string, std::string> keyMap;
        typedef enum {VERSIONS, GRIDINFO, THEORYINFO, BLOB} section;

        // ********************************* Tag Manip *********************************

        template<typename T>
        void AddTag( section sec, std::string const& key, T const& value)
        { AddTag(sec, key,ToString(value)); }
        void AddTag( section sec, std::string const& key, const char* value)
        { AddTag(sec, key,ToString(value));}
        void AddTag( section sec, std::string const& key, std::string const& value);

        // ********************************* Tag Getters *********************************

        bool HasTag( section sec, std::string const& key ) const;
        std::string GetTag( section sec, std::string const& key) const;
        template<typename T> T GetTag( section sec, std::string const& key) const
        { return static_cast<T>(atof(GetTag(sec,key).c_str())); }

    protected:
        void RemTag( section sec, std::string const& key ); //!< Remove existing tags

        // Printing helper functions
        std::string SectionHeader(const char* title, section) const;

        void PrintKeyValue(std::ostream&, section) const;
        void ReadKeyValue( std::istream& is, section sec );

        void PrintBlob(std::ostream& os, std::string blobname) const;
        void ReadBlob(std::istream& is, std::string blobname);

        // Map fetchers helper functions
        section GetSection(std::string const&) const; //!< Fetch the appropriate section for a title
        const keyMap* GetMap(section const& sec) const; //!< Fetch the appropriate map for a section
        keyMap* GetMap(section const& sec)              //!< Fetch the appropriate map for a section
        { return const_cast<keyMap*>(const_cast<const FKHeader*>(this)->GetMap(sec)); };

        // ********************************* Attributes *********************************

        // Key-value pairs
        keyMap fVersions;
        keyMap fGridInfo;
        keyMap fTheoryInfo;
        keyMap fBlobString;

        friend class FKTable;
    };

    /**
    * \class FKTable
    * \brief Class for holding FastKernel tables
    */
    class FKTable
    {
      public:
        FKTable(    std::istream& ,
                    std::vector<std::string> const& cFactors = std::vector<std::string>()
                ); // Stream constructor
        FKTable(    std::string const& filename,
                    std::vector<std::string> const& cfactors = std::vector<std::string>()
                ); // Filename constructor
        FKTable(FKTable const&); //!< Copy constructor
        FKTable(FKTable const&, std::vector<int> const&); //!< Masked copy constructor

        virtual ~FKTable(); //!< Destructor
        void Print(std::ostream&); //!< Print FKTable header to ostream
        void Print(std::string const&, bool const& compress = true);

        // ******************** FK Get Methods ***************************

        std::string const& GetDataName()  const {return fDataName;}

        double const&  GetQ20()      const { return fQ20;   }
        double const*  GetCFactors() const { return fcFactors; }
        double const*  GetCUncerts() const { return fcUncerts; }

        int const&   GetNData()   const { return fNData;}  //!< Return fNData
        int const&   GetNx()      const { return fNx;   }  //!< Return fNx
        int const&   GetTx()      const { return fTx;   }  //!< Return fTx
        int const&   GetDSz()     const { return fDSz;  }  //!< Return fDSz

        double *  GetXGrid() const { return fXgrid;   }  //!< Return fXGrid
        real   *  GetSigma() const { return fSigma;   }  //!< Return fSigma

        int *   GetFlmap()   const { return fFlmap;   }  //!< Return fFlmap
        int const&   GetNonZero() const { return fNonZero; }  //!< Return fNonZero

        bool const& IsHadronic()  const { return fHadronic;}  //!< Return fHadronic

        std::string GetTag(FKHeader::section sec, std::string const& key) const { return fFKHeader.GetTag(sec, key); }

        // GetISig returns a position in the FK table
        int GetISig(  int const& d,     // Datapoint index
                      int const& ix1,   // First x-index
                      int const& ix2,   // Second x-index
                      int const& ifl1,  // First flavour index
                      int const& ifl2   // Second flavour index
                    ) const;

        // DIS version of GetISig
        int GetISig(  int const& d,     // Datapoint index
                      int const& ix,    // x-index
                      int const& ifl    // flavour index
                   ) const;

      protected:
        void ReadCFactors(std::string const& filename); //!< Read C-factors from file
        bool OptimalFlavourmap(std::string& flmap) const; //!< Determine and return the optimal flavour map


        // FKHeader
        FKHeader fFKHeader;

        // Metadata
        std::string fDataName;
        std::string fDescription;
        int   fNData;

        // Process information
        double  fQ20;
        bool  fHadronic;
        int   fNonZero;
        int * fFlmap;

        // x-grid information
        int   fNx;
        int   fTx;
        int   fRmr;
        int   fDSz;

        // X-arrays
        double * fXgrid;

        // FK table
        real * fSigma;

        // Cfactor information and uncertainties
        bool fHasCFactors;
        double * fcFactors;
        double * fcUncerts; // the *squared* uncorrelated uncertainty of the C-factors

      private:
        FKTable();                          //!< Disable default constructor
        FKTable& operator=(const FKTable&); //!< Disable copy-assignment

        void InitialiseFromStream(std::istream&, std::vector<std::string> const& cFactors); //!< Initialise the FK table from an input stream

        int parseNonZero(); // Parse flavourmap information into fNonZero
    };

}
