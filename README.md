//Copyright TRAISTARU Andreea-Maria 332CA

================== Marketplace ===================

----------------- Tema 1 - ASC -------------------

    Implementare.
        
        Modulele folosite sunt: consumer.py, producer.py, marketplace.py
    și product.py(pentru testare). Tema a fost implementata complet.
        În modulul 'producer' este implementată metoda 'run' în care se
    iterează prin lista de produse și se publică în marketplace. Dacă operația
    de publicare eșueaza producătorul respectiv va aștepta pâna sa reîncerce.
        În modulul 'consumer' este implementată metoda 'run' care pentru
    fiecare coș va cere un id de la marketplace și efectuează operațiile specificate.
    Pentru operația de add consumatorul va verifica ce returnează metoda 'add_to_cart'.
    Dacă returnează Fals atunci va aștepta pâna să încerce să îl adauge din nou.

        Marketplace reprezintă modulul principal. Atributele acestei clase sunt:

        -> 2 lock-uri unul folosit pentru accesul consumatorilor, 
        iar altul pentru cel al producătorilor;
        -> un dicționar ce conține produsele ce au fost publicate de către producători;
        cheia este id-ul producătorului, iar valoare este un alt dicționar cu elemente
        de forma (produs, cantitate);
        -> un dicționar ce mapează id-ul unui coș la un dicționar ce conține produsele
        care au fost adăugate în respectivul coș;
        -> un dicționar ce reține pentru fiecare producător câte produse a publicat 
        în marketplace;
        -> 2 întregi unul folosit pentru id-ul producătorilor și altul pentru id-ul
        coșurilor;

        Metodele din marketplace sunt:

        -> register_producer: incrementează id-ul producătorilor și îl returnează; tot aici
        este inițializat dicționarul de produse pe care le va adăuga producătorul respectiv,
        precum și spațiul pe care acesta îl are la dispoziție;

        -> publish: dacă producătorul mai are loc în buffer-ul său, produsul acestuia va
        fi adăugat în dicționarul de produse și va crește numărul de produse publicate
        de producătorul respectiv;

        -> new_cart: incrementează id-ul consumatorilor și îl returnează; tot aici
        este inițializat dicționarul pentru noul coș;

        -> add_to_cart: verifică dacă produsul cerut se află în lista de produse și
        apoi îl elimină dacă există și îl adaugă în dicționarul coșului cu id-ul primit
        ca parametru; 

        -> remove_from_cart: caută produsul în coș, iar apoi îl șterge de acolo și
        îl adaugă la loc în dicționarul de produse;

        -> place_order: printează produsele ce vor fi cumpărate și face loc în
        buffer-ul producătorilor;

    