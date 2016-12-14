self int rec;
self uint64_t st;

pid$1:libpEpEngine:encrypt_message:entry
{
    self->rec = 1;
    self->st = timestamp;
}

pid$1:libpEpEngine:encrypt_message:return
{
    self->rec = 0;
    printf("%d", timestamp - self->st);
}

pid$1:libgpgme::entry,
pid$1:libpEpEngine::entry
/self->rec == 1/
{
    printf("%d", timestamp - self->st);
}

pid$1:libgpgme::return,
pid$1:libpEpEngine::return
/self->rec == 1/
{
    printf("%d", timestamp - self->st);
}

