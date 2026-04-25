export const publicHolidays = {
  // Official GovHK general holidays for 2026, excluding ordinary Sundays.
  2026: [
    "2026-01-01",
    "2026-02-17",
    "2026-02-18",
    "2026-02-19",
    "2026-04-03",
    "2026-04-04",
    "2026-04-06",
    "2026-04-07",
    "2026-05-01",
    "2026-05-25",
    "2026-06-19",
    "2026-07-01",
    "2026-09-26",
    "2026-10-01",
    "2026-10-19",
    "2026-12-25",
    "2026-12-26",
  ],
};

const centralWeekdayFromCentral = [
  "00:00", "00:30", "06:30", "07:00", "07:20", "07:40", "08:00", "08:20", "08:40",
  "09:10", "09:40", "10:10", "10:40", "11:10", "11:40", "12:10", "12:40",
  "13:10", "13:40", "14:10", "14:40", "15:10", "15:30", "15:50", "16:10",
  "16:40", "17:10", "17:40", "18:10", "18:30", "18:50", "19:10", "19:30",
  "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
];

const centralWeekdayFromDb = [
  "00:00", "06:00", "06:30", "06:45", "07:00", "07:15", "07:30", "07:45", "08:00",
  "08:15", "08:30", "08:50", "09:10", "09:40", "10:10", "10:40", "11:10",
  "11:40", "12:10", "12:40", "13:10", "13:40", "14:10", "14:40", "15:10",
  "15:40", "16:10", "16:40", "17:10", "17:40", "18:00", "18:20", "18:40",
  "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
  "23:00", "23:30",
];

const centralSaturdayFromCentral = [
  "00:00", "00:30", "01:00", "06:30", "07:00", "07:30", "08:00", "08:30", "08:50",
  "09:10", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
  "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
  "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
  "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
];

const centralSaturdayFromDb = [
  "00:00", "00:30", "06:00", "06:30", "07:00", "07:20", "07:40", "08:00", "08:15",
  "08:30", "08:45", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
  "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
  "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
  "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
];

const centralSundayFromCentral = [
  "00:00", "00:30", "01:00", "06:30", "07:10", "07:50", "08:30", "09:00", "09:30",
  "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
  "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
  "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
  "22:00", "22:30", "23:00", "23:30",
];

const centralSundayFromDb = [
  "00:00", "00:30", "06:00", "06:40", "07:20", "08:00", "08:30", "09:00", "09:30",
  "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
  "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
  "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30",
  "22:00", "22:30", "23:00", "23:30",
];

const airportBusFromDb = [
  "00:00",
  "01:00",
  "03:00",
  "05:00",
  "06:00",
  "06:30",
  "07:00",
  "07:30",
  "08:00",
  "08:30",
  "09:00",
  "09:30",
  { time: "10:00", note: "Detours via HZMB Hong Kong Port after airport" },
  "11:00",
  "12:00",
  "13:00",
  "14:00",
  "15:00",
  "16:00",
  "17:00",
  "17:30",
  "18:00",
  "18:30",
  "19:00",
  "19:30",
  "20:00",
  "20:30",
  "21:00",
  "21:30",
  "22:00",
  "22:30",
  "23:00",
];

const airportBusFromAirport = [
  "00:30",
  "01:30",
  "03:30",
  "05:30",
  "06:30",
  "07:00",
  "07:30",
  "08:00",
  "08:30",
  "09:00",
  "09:30",
  "10:00",
  { time: "10:45", note: "Departs HZMB Hong Kong Port at about 10:55" },
  "11:45",
  "12:45",
  "13:45",
  "14:45",
  "15:45",
  "16:45",
  { time: "17:30", note: "Via Cathay City" },
  "18:00",
  "18:30",
  "19:00",
  "19:30",
  "20:00",
  "20:30",
  "21:00",
  "21:30",
  "22:00",
  "22:30",
  "23:00",
  "23:30",
];

export const routes = [
  {
    id: "central",
    label: "Central",
    source: {
      text: "Transport Department/Data.gov Central - Discovery Bay XLSX, last updated 22 Aug 2025.",
      url: "https://data.gov.hk/en-data/dataset/hk-td-wcms_8-ferry-services-tt-ft/resource/d45a3f81-2553-4b0c-9429-ee3b2cd71512",
    },
    directions: [
      {
        id: "db-central",
        label: "DB → Central",
        origin: "Discovery Bay",
        destination: "Central",
        schedules: {
          weekday: centralWeekdayFromDb,
          saturday: centralSaturdayFromDb,
          sundayPH: centralSundayFromDb,
        },
      },
      {
        id: "central-db",
        label: "Central → DB",
        origin: "Central",
        destination: "Discovery Bay",
        schedules: {
          weekday: centralWeekdayFromCentral,
          saturday: centralSaturdayFromCentral,
          sundayPH: centralSundayFromCentral,
        },
      },
      {
        id: "dbnorth-central",
        label: "DB North → Central",
        origin: "DB North",
        destination: "Central",
        schedules: {
          weekday: [],
          saturday: [],
          sundayPH: ["10:45", "12:15", "14:45", "17:15"],
        },
      },
      {
        id: "central-dbnorth",
        label: "Central → DB North",
        origin: "Central",
        destination: "DB North",
        schedules: {
          weekday: [],
          saturday: [],
          sundayPH: ["11:30", "13:00", "15:30", "18:00"],
        },
      },
    ],
  },
  {
    id: "muiwo",
    label: "Mui Wo",
    source: {
      text: "Peng Chau Kai To DB - Mui Wo timetable, effective date shown as 1 Jul 2022. Weekday service is via Peng Chau and excludes school holidays.",
      url: "https://en.pengchaukaito.com/ferry-timetable-fare",
    },
    directions: [
      {
        id: "db-muiwo",
        label: "DB → Mui Wo",
        origin: "Discovery Bay",
        destination: "Mui Wo",
        schedules: {
          weekday: [{ time: "15:15", note: "Via Peng Chau" }],
          saturday: ["07:15", "10:45", "13:15", "16:15", "18:15", "20:05"],
          sundayPH: ["08:45", "10:45", "11:45", "13:15", "15:05", "16:15", "18:15", "20:05"],
        },
      },
      {
        id: "muiwo-db",
        label: "Mui Wo → DB",
        origin: "Mui Wo",
        destination: "Discovery Bay",
        schedules: {
          weekday: [{ time: "07:20", note: "Via Peng Chau" }],
          saturday: ["07:45", "11:15", "13:45", "16:45", "18:45", "20:30"],
          sundayPH: ["09:15", "11:15", "12:15", "13:45", "15:35", "16:45", "18:45", "20:30"],
        },
      },
    ],
  },
  {
    id: "pengchau",
    label: "Peng Chau",
    source: {
      text: "Blue Sea Ferry / Transport Department DB - Peng Chau via Trappist Monastery timetable. Some marked sailings go via Trappist Monastery.",
      url: "https://www.blueseaferry.com.hk/en/pc6/",
    },
    directions: [
      {
        id: "db-pengchau",
        label: "DB → Peng Chau",
        origin: "Discovery Bay",
        destination: "Peng Chau",
        schedules: {
          weekday: [
            "06:45", "07:10", { time: "08:00", note: "Via Trappist" }, "08:45",
            { time: "09:20", note: "Via Trappist" }, { time: "10:30", note: "Via Trappist" },
            "11:40", "12:40", "13:20", { time: "14:35", note: "Via Trappist" },
            "16:40", "17:00", "17:30", "18:00", "18:30", "19:00", "20:00",
            "21:00", "22:15",
          ],
          saturday: [
            "06:45", "07:10", { time: "08:00", note: "Via Trappist" }, "08:45",
            { time: "09:20", note: "Via Trappist" }, { time: "10:30", note: "Via Trappist" },
            "11:40", "12:40", "13:20", { time: "14:35", note: "Via Trappist" },
            { time: "15:50", note: "Via Trappist, Saturday only" }, "16:40", "17:00",
            "17:30", "18:00", "18:30", "19:00", "20:00", "21:00", "22:15",
          ],
          sundayPH: [
            "06:45", "07:10", { time: "08:00", note: "Via Trappist" }, "09:00",
            { time: "09:40", note: "Via Trappist" }, "10:40", { time: "11:15", note: "Via Trappist" },
            "12:30", "13:20", "13:50", { time: "14:45", note: "Via Trappist" },
            { time: "15:50", note: "Via Trappist" }, "16:40", "17:30", "18:00", "18:30",
            "19:00", "20:00", "21:00", "22:15",
          ],
        },
      },
      {
        id: "pengchau-db",
        label: "Peng Chau → DB",
        origin: "Peng Chau",
        destination: "Discovery Bay",
        schedules: {
          weekday: [
            "06:30", "07:00", "07:20", "07:45", "08:30", "09:10", "10:15",
            { time: "11:20", note: "Via Trappist" }, { time: "12:20", note: "Via Trappist" },
            "13:00", "14:20", { time: "16:15", note: "Via Trappist" },
            { time: "17:00", note: "Via Trappist" }, "17:45", "18:15", "18:45",
            "19:45", "20:45", "22:00",
          ],
          saturday: [
            "06:30", "07:00", "07:20", "07:45", "08:30", "09:10", "10:15",
            { time: "11:20", note: "Via Trappist" }, { time: "12:20", note: "Via Trappist" },
            "13:00", "14:20", { time: "15:40", note: "Saturday only" },
            { time: "16:15", note: "Via Trappist" }, { time: "17:00", note: "Via Trappist" },
            "17:45", "18:15", "18:45", "19:45", "20:45", "22:00",
          ],
          sundayPH: [
            "06:30", "07:00", "07:45", "08:45", "09:30", { time: "10:15", note: "Via Trappist" },
            "11:00", { time: "12:10", note: "Via Trappist" }, "13:00", "13:35", "14:30",
            "15:40", { time: "16:15", note: "Via Trappist" }, { time: "17:00", note: "Via Trappist" },
            "17:45", "18:15", "18:45", "19:45", "20:45", "22:00",
          ],
        },
      },
    ],
  },
  {
    id: "airport-bus",
    label: "Airport bus",
    source: {
      text: "Discovery Bay Transit Services route DB02R DB Plaza - HK International Airport timetable, effective date shown as 23 Sep 2025.",
      url: "https://www.visitdiscoverybay.com/assets/documents/transportation_bus_ext_db02r.pdf",
    },
    directions: [
      {
        id: "db-airport",
        label: "DB → Airport",
        origin: "Discovery Bay",
        destination: "HK International Airport",
        schedules: {
          weekday: airportBusFromDb,
          saturday: airportBusFromDb,
          sundayPH: airportBusFromDb,
        },
      },
      {
        id: "airport-db",
        label: "Airport → DB",
        origin: "HK International Airport",
        destination: "Discovery Bay",
        schedules: {
          weekday: airportBusFromAirport,
          saturday: airportBusFromAirport,
          sundayPH: airportBusFromAirport,
        },
      },
    ],
  },
];
