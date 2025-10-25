import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from apps.recipes.models import Recipe
from core.utils.bucket import generate_key, put_object

User = get_user_model()

# Predefined recipe data
RECIPES_DATA = [
    {
        "title": "Classic Spaghetti Carbonara",
        "description": "A traditional Italian pasta dish made with eggs, cheese, pancetta, and black pepper. Simple yet delicious.",
        "image_name": "spaghetti_carbonara.jpg",
    },
    {
        "title": "Chicken Tikka Masala",
        "description": "Creamy and spicy curry with tender chicken pieces in a rich tomato-based sauce. Served with rice or naan.",
        "image_name": "chicken_tikka.jpg",
    },
    {
        "title": "Vegetable Stir Fry",
        "description": "Colorful mix of fresh vegetables stir-fried with soy sauce and garlic. Quick and healthy meal.",
        "image_name": "vegetable_stir_fry.jpg",
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Soft and chewy cookies loaded with chocolate chips. Perfect for dessert or snacking.",
        "image_name": "chocolate_chip_cookies.jpg",
    },
    {
        "title": "Greek Salad",
        "description": "Fresh tomatoes, cucumbers, olives, feta cheese, and olive oil dressing. Light and refreshing.",
        "image_name": "greek_salad.jpg",
    },
    {
        "title": "Beef Tacos",
        "description": "Seasoned ground beef in corn tortillas with lettuce, cheese, and salsa. Mexican street food favorite.",
        "image_name": "beef_tacos.jpg",
    },
    {
        "title": "Mushroom Risotto",
        "description": "Creamy Arborio rice cooked with mushrooms, white wine, and Parmesan cheese. Italian comfort food.",
        "image_name": "mushroom_risotto.jpg",
    },
    {
        "title": "Banana Bread",
        "description": "Moist bread made with ripe bananas, walnuts, and cinnamon. Great for breakfast or tea time.",
        "image_name": "banana_bread.jpg",
    },
    {
        "title": "Shakshuka",
        "description": "North African dish of eggs poached in tomato sauce with peppers, onions, and spices. Served with bread.",
        "image_name": "shakshuka.jpg",
    },
    {
        "title": "Caesar Salad",
        "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan cheese. Classic salad.",
        "image_name": "caesar_salad.jpg",
    },
    {
        "title": "Pancakes",
        "description": "Fluffy pancakes served with maple syrup and butter. Perfect weekend breakfast.",
        "image_name": "pancakes.jpg",
    },
    {
        "title": "Lentil Soup",
        "description": "Hearty soup made with lentils, vegetables, and herbs. Comforting and nutritious.",
        "image_name": "lentil_soup.jpg",
    },
    {
        "title": "Apple Pie",
        "description": "Traditional pie with cinnamon-spiced apples in a flaky crust. American classic.",
        "image_name": "apple_pie.jpg",
    },
    {
        "title": "Pad Thai",
        "description": "Thai stir-fried noodles with shrimp, tofu, peanuts, and tamarind sauce. Street food delight.",
        "image_name": "pad_thai.jpg",
    },
    {
        "title": "Quiche Lorraine",
        "description": "Savory pie with bacon, cheese, and eggs in a pastry crust. French brunch favorite.",
        "image_name": "quiche_lorraine.jpg",
    },
    {
        "title": "Tomato Basil Soup",
        "description": "Creamy soup made with fresh tomatoes, basil, and cream. Served with grilled cheese.",
        "image_name": "tomato_basil_soup.jpg",
    },
    {
        "title": "Fried Rice",
        "description": "Chinese-style rice dish with vegetables, eggs, and soy sauce. Quick and versatile.",
        "image_name": "fried_rice.jpg",
    },
    {
        "title": "Brownies",
        "description": "Rich and fudgy chocolate brownies. Indulgent dessert for chocolate lovers.",
        "image_name": "brownies.jpg",
    },
    {
        "title": "Caprese Salad",
        "description": "Simple Italian salad with tomatoes, mozzarella, basil, and balsamic glaze.",
        "image_name": "caprese_salad.jpg",
    },
    {
        "title": "Chicken Curry",
        "description": "Spicy curry with tender chicken, coconut milk, and aromatic spices. Served with rice.",
        "image_name": "chicken_curry.jpg",
    },
]


class Command(BaseCommand):
    help = "Seed the database with initial data: user and recipes with images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset existing data before seeding",
        )

    def _reset_data(self):
        self.stdout.write("Resetting existing data...")
        Recipe.objects.all().delete()
        User.objects.filter(username="tasti").delete()

    def _create_user(self):
        user, created = User.objects.get_or_create(username="tasti", defaults={"is_active": True})
        if created:
            password = get_random_string(length=12)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user "tasti" with password: {password}'))
        else:
            self.stdout.write('User "tasti" already exists')
        return user

    def _get_image_files(self):
        sample_images_dir = os.path.join(os.path.dirname(__file__), "sample_images")
        if not os.path.exists(sample_images_dir):
            self.stdout.write(
                self.style.WARNING("sample_images directory not found. Skipping image uploads.")
            )
            return [], sample_images_dir
        image_files = [
            f
            for f in os.listdir(sample_images_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not image_files:
            self.stdout.write(
                self.style.WARNING("No image files found. Recipes will be created without images.")
            )
        return image_files, sample_images_dir

    def _read_image_data(self, image_path):
        with open(image_path, "rb") as f:
            return f.read()

    def _get_content_type(self, image_name):
        if image_name.lower().endswith(".png"):
            return "image/png"
        else:
            return "image/jpeg"

    def _upload_to_s3_and_update_recipe(self, recipe, bucket_key, image_data, content_type):
        put_object(bucket_key, image_data, content_type)
        recipe.image_bucket_key = bucket_key
        recipe.save(update_fields=["image_bucket_key"])
        self.stdout.write(f'Uploaded image for "{recipe.title}"')

    def _upload_image_for_recipe(self, recipe, image_name, sample_images_dir):
        image_path = os.path.join(sample_images_dir, image_name)
        try:
            image_data = self._read_image_data(image_path)
            bucket_key = generate_key("recipes", image_name)
            content_type = self._get_content_type(image_name)
            self._upload_to_s3_and_update_recipe(recipe, bucket_key, image_data, content_type)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to upload image for "{recipe.title}": {e}')
            )

    def _create_recipes(self, user, image_files, sample_images_dir):
        recipes_created = 0
        for recipe_data in RECIPES_DATA:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data["title"],
                owner=user,
                defaults={"description": recipe_data["description"]},
            )
            if created:
                # Upload image if available
                image_name = recipe_data.get("image_name")
                if image_name and image_name in image_files:
                    self._upload_image_for_recipe(recipe, image_name, sample_images_dir)

                recipes_created += 1
                self.stdout.write(f"Created recipe: {recipe.title}")
        return recipes_created

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_data()
        user = self._create_user()
        image_files, sample_images_dir = self._get_image_files()
        recipes_created = self._create_recipes(user, image_files, sample_images_dir)
        self.stdout.write(
            self.style.SUCCESS(f"Seeding complete. Created {recipes_created} recipes.")
        )
