# Customer Requirements Specification (Lastenheft)  
### Project  
__Name:__ Campus Dual Alternative  
__Portal:__ eigene Gitea-Instanz([git.tfld.de](https://git.tfld.de/Schwarztee/Softwareprojekt))  
__Technologies:__ Python, Django, Jinja2, CSS, MariaDB, JavaScript  
__Persistence:__ DBMS(MariaDB)  
__Copyright:__ Held by the developer of the corresponding module  
__Licence:__ AGPLv3  

## 1 Objective (Zielstellung)
Durch unser Studium an der BA Leipzig sind wir unweigerlich in den Kontakt mit der Studenten-Verwaltungssoftware Campus-Dual in Berührung gekommen. So konnten viele Studenten bereits Erfahrung mit der Qualität der Software eines großen deutschen Softwarekonzerns machen. Die Nutzerschnittstelle ist altbacken, die Webseite lädt langsam. Wichtige Prüfungsangebote werden den Studenten auf Grund bestimmter Richtlinien erst kurz vor knapp angezeigt. Das Problem sei bekannt, eine Änderung konnte noch nicht angestrebt werden. "Softwarefehler - kann man nichts machen!"  

Unser angestrebtes Ziel ist es, die Studentenverwaltung in das aktuelle Jahrhundert zu holen. Das bedeutet, wir wollen einen Ersatz für Campus-Dual entwickeln. Aber nicht nur das. Corona-bedingt wurde vermehrt auf Homeschooling gesetzt. Dabei war die Nutzung vieler Dienste der BA besonders erschwert oder ebenfalls nicht auf dem modernen Stand. Dazu zählt die ewige Problematik der VPN, der Zugriff auf den Fileserv oder die Abgabe von Prüfungsleistungen. Letzteres hat viele Auswüchse gesehen, welche verschieden gut funktionierten. Warum also nicht mal alles unter einen Hut bringen, ohne die einzelnen Aspekte neuzustricken?  

## 2 Requirements (Anforderungen)
- User Management: student, lecturer, organiser as different roles with different rights  
- Examination: creation, enrollment, withdrawal, submission of papers  
- Timetable: create lectures(name, type, duration, lecturer, room, ...) for specific seminar groups; publish to students (Webcal)  
- Notifications: via email; when you can enroll; when a paper is due and not submitted  
- Official Documents: Immatrikulationsbescheinigung, Notenbescheinigung, BAföG-Dokumente  
- Fileserv Integration: via serverside-VPN for specific student; access materials in web browser  
- User Experience: minimal stylesheets, scripts and other runtime dependencies; responsive design  

## 3 Contact (Kontaktinformationen)
| Principal | Contractor |
| ---	    | ---	 |
| Prof. Dr.-Ing. Christian Heller</br>Berufsakademie Sachsen</br>Staatliche Studienakademie Leipzig</br>Schönauer Straße 113 a</br>04207 Leipzig</br>fon: +49-341-42743-415</br>fax: +49-341-42743-331</br>christian.heller@ba-leipzig.de | Max Hohlfeld</br>E-Mail: s5001554@ba-sachsen.de</br></br>Martin Junghans</br>E-Mail: s5001725@ba-sachsen.de|
