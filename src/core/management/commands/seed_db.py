import os
from datetime import timedelta

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
        "duration": timedelta(minutes=30),
        "difficulty": "medium",
        "steps": [
            "Bring a large pot of salted water to boil for the pasta",
            "Cut pancetta into small cubes and fry in a pan until crispy",
            "Beat eggs with grated Parmesan cheese and black pepper in a bowl",
            "Cook spaghetti according to package instructions until al dente",
            "Reserve 1 cup of pasta water, then drain the pasta",
            "Add hot pasta to the pan with pancetta, remove from heat",
            "Quickly stir in the egg mixture, adding pasta water to create a creamy sauce",
            "Serve immediately with extra Parmesan and black pepper",
        ],
    },
    {
        "title": "Chicken Tikka Masala",
        "description": "Creamy and spicy curry with tender chicken pieces in a rich tomato-based sauce. Served with rice or naan.",
        "image_name": "chicken_tikka.jpg",
        "duration": timedelta(minutes=45),
        "difficulty": "medium",
        "steps": [
            "Cut chicken into bite-sized pieces and marinate with yogurt, tikka masala spices, and lemon juice for 30 minutes",
            "Heat oil in a large pan and cook marinated chicken until browned on all sides",
            "Remove chicken and set aside",
            "In the same pan, sauté diced onions until golden brown",
            "Add minced garlic, ginger, and curry spices, cook for 1 minute",
            "Pour in tomato sauce and simmer for 10 minutes",
            "Add cream and return chicken to the pan",
            "Simmer for 15 minutes until chicken is cooked through and sauce thickens",
            "Garnish with fresh cilantro and serve with rice or naan",
        ],
    },
    {
        "title": "Vegetable Stir Fry",
        "description": "Colorful mix of fresh vegetables stir-fried with soy sauce and garlic. Quick and healthy meal.",
        "image_name": "vegetable_stir_fry.jpg",
        "duration": timedelta(minutes=20),
        "difficulty": "easy",
        "steps": [
            "Wash and chop all vegetables into bite-sized pieces (bell peppers, broccoli, carrots, snap peas)",
            "Heat oil in a wok or large pan over high heat",
            "Add minced garlic and ginger, stir-fry for 30 seconds",
            "Add harder vegetables first (carrots, broccoli) and stir-fry for 3 minutes",
            "Add softer vegetables (bell peppers, snap peas) and cook for 2 minutes",
            "Pour in soy sauce and sesame oil, toss to coat",
            "Cook for another minute until vegetables are tender-crisp",
            "Serve hot over rice or noodles",
        ],
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Soft and chewy cookies loaded with chocolate chips. Perfect for dessert or snacking.",
        "image_name": "chocolate_chip_cookies.jpg",
        "duration": timedelta(minutes=30),
        "difficulty": "easy",
        "steps": [
            "Preheat oven to 375°F (190°C) and line baking sheets with parchment paper",
            "Cream together softened butter, white sugar, and brown sugar until fluffy",
            "Beat in eggs and vanilla extract",
            "In a separate bowl, whisk together flour, baking soda, and salt",
            "Gradually mix dry ingredients into wet ingredients until just combined",
            "Fold in chocolate chips",
            "Drop rounded tablespoons of dough onto prepared baking sheets, spacing 2 inches apart",
            "Bake for 10-12 minutes until edges are golden but centers are still soft",
            "Cool on baking sheet for 5 minutes, then transfer to wire rack",
        ],
    },
    {
        "title": "Greek Salad",
        "description": "Fresh tomatoes, cucumbers, olives, feta cheese, and olive oil dressing. Light and refreshing.",
        "image_name": "greek_salad.jpg",
        "duration": timedelta(minutes=15),
        "difficulty": "easy",
        "steps": [
            "Chop tomatoes into wedges",
            "Slice cucumbers into thick half-moons",
            "Thinly slice red onion",
            "Cut bell pepper into strips",
            "Combine vegetables in a large bowl with Kalamata olives",
            "Crumble feta cheese over the top",
            "Drizzle with olive oil and red wine vinegar",
            "Season with dried oregano, salt, and pepper",
            "Toss gently and serve immediately",
        ],
    },
    {
        "title": "Beef Tacos",
        "description": "Seasoned ground beef in corn tortillas with lettuce, cheese, and salsa. Mexican street food favorite.",
        "image_name": "beef_tacos.jpg",
        "duration": timedelta(minutes=30),
        "difficulty": "medium",
        "steps": [
            "Heat oil in a large skillet over medium-high heat",
            "Add ground beef and cook, breaking it up with a spoon until browned",
            "Drain excess fat from the pan",
            "Add taco seasoning, cumin, chili powder, and a splash of water",
            "Simmer for 5 minutes until seasoning is well incorporated",
            "Warm corn tortillas in a dry pan or over a gas flame",
            "Fill each tortilla with seasoned beef",
            "Top with shredded lettuce, diced tomatoes, cheese, and sour cream",
            "Serve with salsa and lime wedges",
        ],
    },
    {
        "title": "Mushroom Risotto",
        "description": "Creamy Arborio rice cooked with mushrooms, white wine, and Parmesan cheese. Italian comfort food.",
        "image_name": "mushroom_risotto.jpg",
        "duration": timedelta(minutes=40),
        "difficulty": "medium",
        "steps": [
            "Heat chicken or vegetable broth in a saucepan and keep warm",
            "Slice mushrooms and sauté in butter until golden, set aside",
            "In a large pan, sauté diced onion in olive oil until translucent",
            "Add Arborio rice and toast for 2 minutes, stirring constantly",
            "Pour in white wine and stir until absorbed",
            "Add warm broth one ladle at a time, stirring frequently until liquid is absorbed before adding more",
            "Continue for 20-25 minutes until rice is creamy and al dente",
            "Stir in sautéed mushrooms, butter, and grated Parmesan cheese",
            "Season with salt and pepper, serve immediately",
        ],
    },
    {
        "title": "Banana Bread",
        "description": "Moist bread made with ripe bananas, walnuts, and cinnamon. Great for breakfast or tea time.",
        "image_name": "banana_bread.jpg",
        "duration": timedelta(minutes=60),
        "difficulty": "easy",
        "steps": [
            "Preheat oven to 350°F (175°C) and grease a 9x5 inch loaf pan",
            "Mash 3-4 very ripe bananas in a large bowl",
            "Mix in melted butter, beaten eggs, vanilla extract, and sugar",
            "In a separate bowl, whisk together flour, baking soda, cinnamon, and salt",
            "Fold dry ingredients into banana mixture until just combined",
            "Stir in chopped walnuts if desired",
            "Pour batter into prepared loaf pan",
            "Bake for 50-60 minutes until a toothpick inserted in center comes out clean",
            "Cool in pan for 10 minutes, then turn out onto wire rack",
        ],
    },
    {
        "title": "Shakshuka",
        "description": "North African dish of eggs poached in tomato sauce with peppers, onions, and spices. Served with bread.",
        "image_name": "shakshuka.jpg",
        "duration": timedelta(minutes=30),
        "difficulty": "medium",
        "steps": [
            "Heat olive oil in a large skillet over medium heat",
            "Sauté diced onions and bell peppers until soft",
            "Add minced garlic, cumin, paprika, and cayenne pepper, cook for 1 minute",
            "Pour in crushed tomatoes and simmer for 10 minutes until sauce thickens",
            "Season with salt and pepper",
            "Make 4-6 wells in the sauce with a spoon",
            "Crack an egg into each well",
            "Cover and cook for 5-8 minutes until egg whites are set but yolks are still runny",
            "Garnish with fresh parsley and feta cheese, serve with crusty bread",
        ],
    },
    {
        "title": "Caesar Salad",
        "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan cheese. Classic salad.",
        "image_name": "caesar_salad.jpg",
        "duration": timedelta(minutes=15),
        "difficulty": "easy",
        "steps": [
            "Wash and dry romaine lettuce, tear into bite-sized pieces",
            "Make Caesar dressing by whisking together mayonnaise, lemon juice, Dijon mustard, minced garlic, and anchovy paste",
            "Add grated Parmesan cheese to the dressing",
            "Season dressing with salt and black pepper",
            "Toss lettuce with dressing in a large bowl",
            "Add croutons and toss again",
            "Top with shaved Parmesan cheese",
            "Serve immediately",
        ],
    },
    {
        "title": "Pancakes",
        "description": "Fluffy pancakes served with maple syrup and butter. Perfect weekend breakfast.",
        "image_name": "pancakes.jpg",
        "duration": timedelta(minutes=20),
        "difficulty": "easy",
        "steps": [
            "Whisk together flour, sugar, baking powder, and salt in a large bowl",
            "In another bowl, beat together milk, eggs, melted butter, and vanilla extract",
            "Pour wet ingredients into dry ingredients and stir until just combined (lumps are okay)",
            "Let batter rest for 5 minutes",
            "Heat a griddle or non-stick pan over medium heat and lightly grease",
            "Pour 1/4 cup batter for each pancake",
            "Cook until bubbles form on surface and edges look set, about 2-3 minutes",
            "Flip and cook for another 1-2 minutes until golden brown",
            "Serve hot with butter and maple syrup",
        ],
    },
    {
        "title": "Lentil Soup",
        "description": "Hearty soup made with lentils, vegetables, and herbs. Comforting and nutritious.",
        "image_name": "lentil_soup.jpg",
        "duration": timedelta(minutes=60),
        "difficulty": "easy",
        "steps": [
            "Rinse and sort through dried lentils, removing any debris",
            "Heat olive oil in a large pot over medium heat",
            "Sauté diced onions, carrots, and celery until softened",
            "Add minced garlic, cumin, and thyme, cook for 1 minute",
            "Add lentils, vegetable broth, and bay leaves",
            "Bring to a boil, then reduce heat and simmer for 30-40 minutes",
            "Add diced tomatoes and spinach in the last 10 minutes",
            "Season with salt, pepper, and a splash of lemon juice",
            "Remove bay leaves and serve hot with crusty bread",
        ],
    },
    {
        "title": "Apple Pie",
        "description": "Traditional pie with cinnamon-spiced apples in a flaky crust. American classic.",
        "image_name": "apple_pie.jpg",
        "duration": timedelta(minutes=90),
        "difficulty": "medium",
        "steps": [
            "Prepare or thaw pie crusts for top and bottom",
            "Peel, core, and slice apples thinly",
            "Toss apples with sugar, cinnamon, nutmeg, lemon juice, and flour",
            "Roll out bottom crust and place in a 9-inch pie pan",
            "Fill with apple mixture and dot with butter",
            "Cover with top crust, crimp edges to seal, and cut slits for venting",
            "Brush top with egg wash and sprinkle with sugar",
            "Bake at 425°F (220°C) for 15 minutes",
            "Reduce heat to 350°F (175°C) and bake for 45-50 minutes until golden brown",
            "Cool for at least 2 hours before slicing",
        ],
    },
    {
        "title": "Pad Thai",
        "description": "Thai stir-fried noodles with shrimp, tofu, peanuts, and tamarind sauce. Street food delight.",
        "image_name": "pad_thai.jpg",
        "duration": timedelta(minutes=25),
        "difficulty": "medium",
        "steps": [
            "Soak rice noodles in warm water for 30 minutes until soft, then drain",
            "Make sauce by mixing tamarind paste, fish sauce, sugar, and lime juice",
            "Heat oil in a wok over high heat",
            "Scramble eggs in the wok, then set aside",
            "Stir-fry shrimp or chicken until cooked through, set aside",
            "Add garlic and tofu to wok, fry until golden",
            "Add drained noodles and sauce, toss quickly",
            "Add bean sprouts, scrambled eggs, and cooked protein, toss together",
            "Serve topped with crushed peanuts, lime wedges, and fresh cilantro",
        ],
    },
    {
        "title": "Quiche Lorraine",
        "description": "Savory pie with bacon, cheese, and eggs in a pastry crust. French brunch favorite.",
        "image_name": "quiche_lorraine.jpg",
        "duration": timedelta(minutes=60),
        "difficulty": "medium",
        "steps": [
            "Preheat oven to 375°F (190°C)",
            "Roll out pie dough and press into a 9-inch tart pan",
            "Blind bake the crust for 15 minutes with pie weights",
            "Cook bacon until crispy, then crumble",
            "Whisk together eggs, heavy cream, salt, pepper, and nutmeg",
            "Sprinkle bacon and grated Gruyère cheese in the pre-baked crust",
            "Pour egg mixture over bacon and cheese",
            "Bake for 30-35 minutes until filling is set and top is golden",
            "Cool for 10 minutes before slicing and serving",
        ],
    },
    {
        "title": "Tomato Basil Soup",
        "description": "Creamy soup made with fresh tomatoes, basil, and cream. Served with grilled cheese.",
        "image_name": "tomato_basil_soup.jpg",
        "duration": timedelta(minutes=40),
        "difficulty": "easy",
        "steps": [
            "Heat olive oil in a large pot over medium heat",
            "Sauté diced onions and minced garlic until soft and fragrant",
            "Add whole or crushed tomatoes with their juice",
            "Add vegetable broth, sugar, and dried oregano",
            "Bring to a boil, then reduce heat and simmer for 20 minutes",
            "Add fresh basil leaves",
            "Use an immersion blender to puree soup until smooth (or transfer to blender in batches)",
            "Stir in heavy cream and warm through",
            "Season with salt and pepper, serve hot with crusty bread or grilled cheese",
        ],
    },
    {
        "title": "Fried Rice",
        "description": "Chinese-style rice dish with vegetables, eggs, and soy sauce. Quick and versatile.",
        "image_name": "fried_rice.jpg",
        "duration": timedelta(minutes=20),
        "difficulty": "easy",
        "steps": [
            "Use day-old cooked rice (freshly cooked rice will be too sticky)",
            "Heat oil in a wok or large pan over high heat",
            "Scramble beaten eggs in the wok, then set aside",
            "Add more oil and stir-fry diced vegetables (carrots, peas, corn)",
            "Add cold rice, breaking up any clumps",
            "Stir-fry for 3-4 minutes until rice is heated through",
            "Add soy sauce and sesame oil, toss to coat",
            "Return scrambled eggs to the wok and mix",
            "Garnish with sliced green onions and serve hot",
        ],
    },
    {
        "title": "Brownies",
        "description": "Rich and fudgy chocolate brownies. Indulgent dessert for chocolate lovers.",
        "image_name": "brownies.jpg",
        "duration": timedelta(minutes=45),
        "difficulty": "easy",
        "steps": [
            "Preheat oven to 350°F (175°C) and grease a 9x13 inch baking pan",
            "Melt butter and chocolate together in a double boiler or microwave",
            "Stir in sugar until well combined",
            "Beat in eggs one at a time, then add vanilla extract",
            "Sift in flour, cocoa powder, and salt, fold until just combined",
            "Fold in chocolate chips if desired",
            "Pour batter into prepared pan and spread evenly",
            "Bake for 25-30 minutes until a toothpick inserted comes out with moist crumbs",
            "Cool completely in pan before cutting into squares",
        ],
    },
    {
        "title": "Caprese Salad",
        "description": "Simple Italian salad with tomatoes, mozzarella, basil, and balsamic glaze.",
        "image_name": "caprese_salad.jpg",
        "duration": timedelta(minutes=10),
        "difficulty": "easy",
        "steps": [
            "Slice ripe tomatoes into 1/4 inch thick rounds",
            "Slice fresh mozzarella into similar sized rounds",
            "Arrange tomato and mozzarella slices alternating on a platter",
            "Tuck fresh basil leaves between the slices",
            "Drizzle with extra virgin olive oil",
            "Drizzle with balsamic glaze or aged balsamic vinegar",
            "Season with flaky sea salt and freshly cracked black pepper",
            "Serve immediately at room temperature",
        ],
    },
    {
        "title": "Chicken Curry",
        "description": "Spicy curry with tender chicken, coconut milk, and aromatic spices. Served with rice.",
        "image_name": "chicken_curry.jpg",
        "duration": timedelta(minutes=50),
        "difficulty": "hard",
        "steps": [
            "Cut chicken thighs into bite-sized pieces",
            "Heat oil in a large pot and brown chicken in batches, set aside",
            "In the same pot, sauté diced onions until golden",
            "Add minced garlic, ginger, and curry powder, cook for 2 minutes",
            "Add tomato paste and cook for 1 minute",
            "Return chicken to pot and stir to coat with spices",
            "Pour in coconut milk and chicken broth",
            "Add diced potatoes and simmer for 25-30 minutes until chicken is tender",
            "Stir in garam masala and fresh cilantro",
            "Season with salt and serve over basmati rice with naan bread",
        ],
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
        user, created = User.objects.get_or_create(
            username="tasti", defaults={"is_active": True}
        )
        if created:
            password = get_random_string(length=12)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created user "tasti" with password: {password}')
            )
        else:
            self.stdout.write('User "tasti" already exists')
        return user

    def _get_image_files(self):
        sample_images_dir = os.path.join(os.path.dirname(__file__), "sample_images")
        if not os.path.exists(sample_images_dir):
            self.stdout.write(
                self.style.WARNING(
                    "sample_images directory not found. Skipping image uploads."
                )
            )
            return [], sample_images_dir
        image_files = [
            f
            for f in os.listdir(sample_images_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not image_files:
            self.stdout.write(
                self.style.WARNING(
                    "No image files found. Recipes will be created without images."
                )
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

    def _upload_to_s3_and_update_recipe(
        self, recipe, bucket_key, image_data, content_type
    ):
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
            self._upload_to_s3_and_update_recipe(
                recipe, bucket_key, image_data, content_type
            )
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
                defaults={
                    "description": recipe_data["description"],
                    "duration": recipe_data["duration"],
                    "difficulty": recipe_data["difficulty"],
                    "steps": recipe_data.get("steps", []),
                },
            )
            if created:
                # Upload image if available
                image_name = recipe_data.get("image_name")
                if image_name and image_name in image_files:
                    self._upload_image_for_recipe(recipe, image_name, sample_images_dir)

                recipes_created += 1
                self.stdout.write(f"Created recipe: {recipe.title}")
            else:
                recipe.duration = recipe_data["duration"]
                recipe.difficulty = recipe_data["difficulty"]
                recipe.steps = recipe_data.get("steps", [])
                recipe.save(update_fields=["duration", "difficulty", "steps"])
                self.stdout.write(f"Updated recipe: {recipe.title}")
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
