CREATE TABLE Members (
    MemberID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(50), 
    ContactNumber VARCHAR(15)
);

CREATE TABLE Trainers (
    TrainerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(50),
    Phone VARCHAR(15)
);

CREATE TABLE Staffs (
    StaffID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(50),
    Phone VARCHAR(15)
);

CREATE TABLE TrainerSchedules (
    ScheduleID SERIAL PRIMARY KEY,
    TrainerID INT,
    AvailableFrom DATE,
    AvailableUntil DATE,
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID)
);

CREATE TABLE RoomBookings (
    BookingID SERIAL PRIMARY KEY,
    RoomID INT,
    StartTime DATE,
    EndTime DATE,
    Description TEXT,
    StaffID INT,
    FOREIGN KEY (StaffID) REFERENCES Staffs(StaffID)
);

CREATE TABLE ClassSchedules (
    ClassID SERIAL PRIMARY KEY,
    StartTime DATE,
    EndTime DATE,
    RoomID INT,
    TrainerID INT,
    FOREIGN KEY (RoomID) REFERENCES RoomBookings(BookingID),
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID)
);

CREATE TABLE ClassRegistrations (
    RegistrationID SERIAL PRIMARY KEY,
    ClassID INT,
    MemberID INT,
    RegistrationDate DATE,
    FOREIGN KEY (ClassID) REFERENCES ClassSchedules(ScheduleID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

CREATE TABLE FitnessGoals (
    GoalID SERIAL PRIMARY KEY,
    MemberID INT,
    WeightGoalKG DECIMAL,
    TimeGoalMonths INT,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

CREATE TABLE HealthMetrics (
    MetricID SERIAL PRIMARY KEY,
    MemberID INT,
    WeightKG DECIMAL(5, 2),
    HeightCM INT,
    RecordedDate DATE,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

CREATE TABLE PersonalTrainingSessions (
    SessionID SERIAL PRIMARY KEY,
    MemberID INT,
    TrainerID INT,
    SessionDate DATE,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID)
);

CREATE TABLE EquipmentMaintenance (
    MaintenanceID SERIAL PRIMARY KEY,
    EquipmentID INT,
    MaintenanceDate DATE,
    Description TEXT,
    IsResolved BOOLEAN DEFAULT FALSE,
    StaffID INT,
    FOREIGN KEY (StaffID) REFERENCES Staffs(StaffID)
);

CREATE TABLE BillingPayments (
    TransactionID SERIAL PRIMARY KEY,
    MemberID INT,
    Amount DECIMAL(10, 2),
    TransactionDate DATE,
    PaymentStatus VARCHAR(20),
    Description TEXT,
    StaffID INT,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (StaffID) REFERENCES Staffs(StaffID)
);

INSERT INTO Trainers (FirstName, LastName, Email, Password, Phone) VALUES
('John', 'Doe', 'johndoe@example.com', 'johndoe', '2001'),
('Jane', 'Smith', 'janesmith@gmail.com', 'janesmith', '2002');
