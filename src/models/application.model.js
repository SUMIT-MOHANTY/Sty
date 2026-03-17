const mongoose = require('mongoose');

const StatusHistorySchema = new mongoose.Schema({
  status: {
    type: String,
    enum: ['pending', 'reviewing', 'approved', 'rejected'],
    required: true
  },
  changedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  comments: {
    type: String
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

const ApplicationSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'User ID is required']
  },
  applicationType: {
    type: String,
    enum: ['new', 'renewal', 'replacement', 'name-change'],
    required: [true, 'Application type is required']
  },
  personalDetails: {
    firstName: {
      type: String,
      required: [true, 'First name is required'],
      minlength: 2,
      maxlength: 50
    },
    middleName: {
      type: String,
      maxlength: 50
    },
    lastName: {
      type: String,
      required: [true, 'Last name is required'],
      minlength: 2,
      maxlength: 50
    },
    dateOfBirth: {
      type: Date,
      required: [true, 'Date of birth is required']
    },
    gender: {
      type: String,
      enum: ['male', 'female', 'other'],
      required: [true, 'Gender is required']
    },
    placeOfBirth: {
      type: String,
      required: [true, 'Place of birth is required'],
      minlength: 2,
      maxlength: 100
    },
    nationality: {
      type: String,
      required: [true, 'Nationality is required'],
      minlength: 2,
      maxlength: 50
    }
  },
  contactDetails: {
    email: {
      type: String,
      required: [true, 'Email is required'],
      match: [
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
        'Please provide a valid email'
      ]
    },
    phone: {
      type: String,
      required: [true, 'Phone number is required'],
      minlength: 10
    },
    address: {
      street: {
        type: String,
        required: [true, 'Street address is required'],
        minlength: 5,
        maxlength: 100
      },
      city: {
        type: String,
        required: [true, 'City is required'],
        minlength: 2,
        maxlength: 50
      },
      state: {
        type: String,
        required: [true, 'State/Province is required'],
        minlength: 2,
        maxlength: 50
      },
      postalCode: {
        type: String,
        required: [true, 'Postal/Zip code is required'],
        minlength: 2,
        maxlength: 20
      },
      country: {
        type: String,
        required: [true, 'Country is required'],
        minlength: 2,
        maxlength: 50
      }
    }
  },
  documents: {
    idProof: {
      documentType: {
        type: String,
        enum: ['national-id', 'drivers-license', 'social-security', 'other'],
        required: [true, 'ID proof type is required']
      },
      documentNumber: {
        type: String,
        required: [true, 'Document number is required']
      },
      documentImage: {
        type: String,
        required: [true, 'Document image URL is required']
      },
      verified: {
        type: Boolean,
        default: false
      }
    },
    photo: {
      type: String,
      required: [true, 'Passport photo is required']
    },
    additionalDocuments: [{
      documentType: {
        type: String,
        required: true
      },
      documentImage: {
        type: String,
        required: true
      },
      verified: {
        type: Boolean,
        default: false
      }
    }]
  },
  travelDetails: {
    purposeOfTravel: {
      type: String,
      required: [true, 'Purpose of travel is required']
    },
    countriesVisiting: [{
      type: String,
      required: true
    }],
    expectedDeparture: {
      type: Date
    }
  },
  emergencyContact: {
    name: {
      type: String,
      required: [true, 'Emergency contact name is required']
    },
    relationship: {
      type: String,
      required: [true, 'Relationship is required']
    },
    phone: {
      type: String,
      required: [true, 'Emergency contact phone is required']
    },
    email: {
      type: String
    }
  },
  status: {
    type: String,
    enum: ['pending', 'reviewing', 'approved', 'rejected'],
    default: 'pending'
  },
  paymentStatus: {
    type: String,
    enum: ['unpaid', 'processing', 'paid', 'refunded'],
    default: 'unpaid'
  },
  paymentDetails: {
    amount: {
      type: Number
    },
    currency: {
      type: String,
      default: 'USD'
    },
    paymentMethod: {
      type: String
    },
    transactionId: {
      type: String
    },
    paymentDate: {
      type: Date
    }
  },
  adminComments: {
    type: String
  },
  lastUpdatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  statusHistory: [StatusHistorySchema],
  appointmentDate: {
    type: Date
  },
  passportDetails: {
    passportNumber: {
      type: String
    },
    issueDate: {
      type: Date
    },
    expiryDate: {
      type: Date
    }
  }
}, { timestamps: true });

// Add text indexes for search
ApplicationSchema.index({
  'personalDetails.firstName': 'text',
  'personalDetails.lastName': 'text',
  'contactDetails.email': 'text',
  'documents.idProof.documentNumber': 'text'
});

module.exports = mongoose.model('Application', ApplicationSchema);
