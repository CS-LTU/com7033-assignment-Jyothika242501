class PatientService:
    def __init__(self, mongo):
        self.collection = mongo["patients"]

    def get_all(self):
        return list(self.collection.find({}))

    def get_by_id(self, patient_id):
        from bson import ObjectId
        return self.collection.find_one({"_id": ObjectId(patient_id)})

    def count_all(self):
        return self.collection.count_documents({})

    def count_stroke(self):
        return self.collection.count_documents({"stroke": 1})

    def count_hypertension(self):
        return self.collection.count_documents({"hypertension": 1})

    def count_heart_disease(self):
        return self.collection.count_documents({"heart_disease": 1})

    def gender_chart(self):
        return list(self.collection.aggregate([
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]))

    def heart_disease_chart(self):
        return list(self.collection.aggregate([
            {"$group": {"_id": "$heart_disease", "count": {"$sum": 1}}}
        ]))
