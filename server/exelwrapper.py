from openpyxl import load_workbook

def indExl(index):
    """Convert 0-based column index to Excel column name (e.g., 0 -> A, 27 -> AB)"""
    cname = ""
    while index >= 0:
        cname = chr(index % 26 + ord('A')) + cname
        index = index // 26 - 1
    return cname

def genTups(path):
    sheet = load_workbook(path).active
    participants = []
    schools = []
    school_ids = set()  # To avoid duplicate school entries
    headers = {}
    columnN = 0
    cell = "A1"

    while sheet[cell].value and "participant" not in sheet[cell].value.lower():
        header = None
        match sheet[cell].value.lower():
            case "email address":
                header = "subEmail"
            case "email":
                header = "email"
            case "school name":
                header = "sName"
            case "school branch/address":
                header = "sAddress"
            case "name of principal":
                header = "pName"
            case "school phone number":
                header = "sPhone"
            case "school email address":
                header = "sEmail"
            case "name of teacher incharge":
                header = "tName"
            case "phone number of teacher incharge":
                header = "tPhone"
            case "email-id of teacher incharge":
                header = "tEmail"
        if header:
            headers[header] = indExl(columnN)
        columnN += 1
        cell = indExl(columnN) + "1"

    pHeaders = {}
    while sheet[cell].value:
        hName = sheet[cell].value.strip()
        pHeaders[hName] = indExl(columnN)
        columnN += 1
        cell = indExl(columnN) + "1"

    row = 2
    pid = 1000
    cell = headers['subEmail'] + str(row)

    while sheet[cell].value:
        sid = "S25" + str(100 + row)
        sName = sheet[headers["sName"] + str(row)].value

        # --- SCHOOL TUPLE ---
        if sid not in school_ids:
            try:
                sTup = (
                    sid,
                    sheet[headers["subEmail"] + str(row)].value,
                    sName,
                    sheet[headers["sAddress"] + str(row)].value,
                    sheet[headers["pName"] + str(row)].value,
                    int(sheet[headers["sPhone"] + str(row)].value),
                    sheet[headers["sEmail"] + str(row)].value,
                    sheet[headers["tName"] + str(row)].value,
                    int(sheet[headers["tPhone"] + str(row)].value),
                    sheet[headers["tEmail"] + str(row)].value
                )
                schools.append(sTup)
                school_ids.add(sid)
            except Exception as e:
                print(f"Skipping invalid school at row {row}: {e}")

        # --- PARTICIPANTS ---
        for pHeader in pHeaders:
            if "name of participant" in pHeader.lower():
                try:
                    parts = pHeader.split("Name of Participant")
                    event = parts[0].strip()
                    pnum = parts[1].strip()
                    clss = f"{event} Class of Participant {pnum}"
                except:
                    continue
                if clss not in pHeaders:
                    continue
                nCell = pHeaders[pHeader] + str(row)
                cCell = pHeaders[clss] + str(row)
                name = sheet[nCell].value
                pClass = sheet[cCell].value
                if name:
                    try:
                        pTup = (
                            pid,
                            name.strip(),
                            int(''.join(filter(str.isdigit, str(pClass)))),  # clean class
                            event.strip(),
                            sid,
                            sName.strip(),
                            False
                        )
                        participants.append(pTup)
                        pid += 1
                    except Exception as e:
                        print(f"Skipping participant at row {row}: {e}")

        row += 1
        cell = headers['subEmail'] + str(row)

    return schools, participants

