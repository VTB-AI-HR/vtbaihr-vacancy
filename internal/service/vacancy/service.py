from internal import interface


class VacancyService(interface.IVacancyService):
    def __init__(
            self,
            vacancy_repo: interface.IVacancyRepo,
    ):
        self.vacancy_repo = vacancy_repo