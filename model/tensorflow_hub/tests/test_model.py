import sys
import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.source.source import Sources
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Data, Feature, Features, DefFeature
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml_model_tensorflow_hub.text_classifier import (
    TextClassificationModel,
    TextClassifierConfig,
)


class TestTextClassificationModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.features = Features()
        cls.features.append(DefFeature("A", str, 1))
        A, X = list(zip(*DATA))
        cls.repos = [
            Repo(str(i), data={"features": {"A": A[i], "X": X[i],}},)
            for i in range(0, len(X))
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = TextClassificationModel(
            TextClassifierConfig(
                directory=cls.model_dir.name,
                classifications=[0, 1],
                features=cls.features,
                predict=DefFeature("X", int, 1),
                add_layers=True,
                layers=[
                    "Dense(16, activation='relu')",
                    "Dense(2, activation='softmax')",
                ],
                model_path="https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1",
                embedType="swivel",
                epochs=30,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                self.assertGreater(res, 0)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                async for repo in mctx.predict(sctx.repos()):
                    prediction = repo.prediction().value
                    self.assertIn(prediction, ["0", "1"])


DATA = [
    [
        "This was an absolutely terrible movie. Don't be lured in by Christopher Walken or Michael Ironside. Both are great actors, but this must simply be their worst role in history. Even their great acting could not redeem this movie's ridiculous storyline. This movie is an early nineties US propaganda piece. The most pathetic scenes were those when the Columbian rebels were making their cases for revolutions. Maria Conchita Alonso appeared phony, and her pseudo-love affair with Walken was nothing but a pathetic emotional plug in a movie that was devoid of any real meaning. I am disappointed that there are movies like this, ruining actor's like Christopher Walken's good name. I could barely sit through it.",
        "0",
    ],
    [
        "I have been known to fall asleep during films, but this is usually due to a combination of things including, really tired, being warm and comfortable on the sette and having just eaten a lot. However on this occasion I fell asleep because the film was rubbish. The plot development was constant. Constantly slow and boring. Things seemed to happen, but with no explanation of what was causing them or why. I admit, I may have missed part of the film, but i watched the majority of it and everything just seemed to happen of its own accord without any real concern for anything else. I cant recommend this film at all.",
        "0",
    ],
    [
        "Mann photographs the Alberta Rocky Mountains in a superb fashion, and Jimmy Stewart and Walter Brennan give enjoyable performances as they always seem to do. <br /><br />But come on Hollywood - a Mountie telling the people of Dawson City, Yukon to elect themselves a marshal (yes a marshal!) and to enforce the law themselves, then gunfighters battling it out on the streets for control of the town? <br /><br />Nothing even remotely resembling that happened on the Canadian side of the border during the Klondike gold rush. Mr. Mann and company appear to have mistaken Dawson City for Deadwood, the Canadian North for the American Wild West.<br /><br />Canadian viewers be prepared for a Reefer Madness type of enjoyable howl with this ludicrous plot, or, to shake your head in disgust.",
        "0",
    ],
    [
        "This is the kind of film for a snowy Sunday afternoon when the rest of the world can go ahead with its own business as you descend into a big arm-chair and mellow for a couple of hours. Wonderful performances from Cher and Nicolas Cage (as always) gently row the plot along. There are no rapids to cross, no dangerous waters, just a warm and witty paddle through New York life at its best. A family film in every sense and one that deserves the praise it received.",
        "1",
    ],
    [
        'As others have mentioned, all the women that go nude in this film are mostly absolutely gorgeous. The plot very ably shows the hypocrisy of the female libido. When men are around they want to be pursued, but when no "men" are around, they become the pursuers of a 14 year old boy. And the boy becomes a man really fast (we should all be so lucky at this age!). He then gets up the courage to pursue his true love.',
        "1",
    ],
    [
        "This is a film which should be seen by anybody interested in, effected by, or suffering from an eating disorder. It is an amazingly accurate and sensitive portrayal of bulimia in a teenage girl, its causes and its symptoms. The girl is played by one of the most brilliant young actresses working in cinema today, Alison Lohman, who was later so spectacular in 'Where the Truth Lies'. I would recommend that this film be shown in all schools, as you will never see a better on this subject. Alison Lohman is absolutely outstanding, and one marvels at her ability to convey the anguish of a girl suffering from this compulsive disorder. If barometers tell us the air pressure, Alison Lohman tells us the emotional pressure with the same degree of accuracy. Her emotional range is so precise, each scene could be measured microscopically for its gradations of trauma, on a scale of rising hysteria and desperation which reaches unbearable intensity. Mare Winningham is the perfect choice to play her mother, and does so with immense sympathy and a range of emotions just as finely tuned as Lohman's. Together, they make a pair of sensitive emotional oscillators vibrating in resonance with one another. This film is really an astonishing achievement, and director Katt Shea should be proud of it. The only reason for not seeing it is if you are not interested in people. But even if you like nature films best, this is after all animal behaviour at the sharp edge. Bulimia is an extreme version of how a tormented soul can destroy her own body in a frenzy of despair. And if we don't sympathise with people suffering from the depths of despair, then we are dead inside.",
        "1",
    ],
    [
        "Okay, you have:<br /><br />Penelope Keith as Miss Herringbone-Tweed, B.B.E. (Backbone of England.) She's killed off in the first scene - that's right, folks; this show has no backbone!<br /><br />Peter O'Toole as Ol' Colonel Cricket from The First War and now the emblazered Lord of the Manor.<br /><br />Joanna Lumley as the ensweatered Lady of the Manor, 20 years younger than the colonel and 20 years past her own prime but still glamourous (Brit spelling, not mine) enough to have a toy-boy on the side. It's alright, they have Col. Cricket's full knowledge and consent (they guy even comes 'round for Christmas!) Still, she's considerate of the colonel enough to have said toy-boy her own age (what a gal!)<br /><br />David McCallum as said toy-boy, equally as pointlessly glamourous as his squeeze. Pilcher couldn't come up with any cover for him within the story, so she gave him a hush-hush job at the Circus.<br /><br />and finally:<br /><br />Susan Hampshire as Miss Polonia Teacups, Venerable Headmistress of the Venerable Girls' Boarding-School, serving tea in her office with a dash of deep, poignant advice for life in the outside world just before graduation. Her best bit of advice: \"I've only been to Nancherrow (the local Stately Home of England) once. I thought it was very beautiful but, somehow, not part of the real world.\" Well, we can't say they didn't warn us.<br /><br />Ah, Susan - time was, your character would have been running the whole show. They don't write 'em like that any more. Our loss, not yours.<br /><br />So - with a cast and setting like this, you have the re-makings of \"Brideshead Revisited,\" right?<br /><br />Wrong! They took these 1-dimensional supporting roles because they paid so well. After all, acting is one of the oldest temp-jobs there is (YOU name another!)<br /><br />First warning sign: lots and lots of backlighting. They get around it by shooting outdoors - \"hey, it's just the sunlight!\"<br /><br />Second warning sign: Leading Lady cries a lot. When not crying, her eyes are moist. That's the law of romance novels: Leading Lady is \"dewy-eyed.\"<br /><br />Henceforth, Leading Lady shall be known as L.L.<br /><br />Third warning sign: L.L. actually has stars in her eyes when she's in love. Still, I'll give Emily Mortimer an award just for having to act with that spotlight in her eyes (I wonder . did they use contacts?)<br /><br />And lastly, fourth warning sign: no on-screen female character is \"Mrs.\" She's either \"Miss\" or \"Lady.\"<br /><br />When all was said and done, I still couldn't tell you who was pursuing whom and why. I couldn't even tell you what was said and done.<br /><br />To sum up: they all live through World War II without anything happening to them at all.<br /><br />OK, at the end, L.L. finds she's lost her parents to the Japanese prison camps and baby sis comes home catatonic. Meanwhile (there's always a \"meanwhile,\") some young guy L.L. had a crush on (when, I don't know) comes home from some wartime tough spot and is found living on the street by Lady of the Manor (must be some street if SHE's going to find him there.) Both war casualties are whisked away to recover at Nancherrow (SOMEBODY has to be \"whisked away\" SOMEWHERE in these romance stories!)<br /><br />Great drama.",
        "0",
    ],
    [
        'The film is based on a genuine 1950s novel.<br /><br />Journalist Colin McInnes wrote a set of three "London novels": "Absolute Beginners", "City of Spades" and "Mr Love and Justice". I have read all three. The first two are excellent. The last, perhaps an experiment that did not come off. But McInnes\'s work is highly acclaimed; and rightly so. This musical is the novelist\'s ultimate nightmare - to see the fruits of one\'s mind being turned into a glitzy, badly-acted, soporific one-dimensional apology of a film that says it captures the spirit of 1950s London, and does nothing of the sort.<br /><br />Thank goodness Colin McInnes wasn\'t alive to witness it.',
        "0",
    ],
    [
        "I really love the sexy action and sci-fi films of the sixties and its because of the actress's that appeared in them. They found the sexiest women to be in these films and it didn't matter if they could act (Remember \"Candy\"?). The reason I was disappointed by this film was because it wasn't nostalgic enough. The story here has a European sci-fi film called \"Dragonfly\" being made and the director is fired. So the producers decide to let a young aspiring filmmaker (Jeremy Davies) to complete the picture. They're is one real beautiful woman in the film who plays Dragonfly but she's barely in it. Film is written and directed by Roman Coppola who uses some of his fathers exploits from his early days and puts it into the script. I wish the film could have been an homage to those early films. They could have lots of cameos by actors who appeared in them. There is one actor in this film who was popular from the sixties and its John Phillip Law (Barbarella). Gerard Depardieu, Giancarlo Giannini and Dean Stockwell appear as well. I guess I'm going to have to continue waiting for a director to make a good homage to the films of the sixties. If any are reading this, \"Make it as sexy as you can\"! I'll be waiting!",
        "0",
    ],
    [
        'Sure, this one isn\'t really a blockbuster, nor does it target such a position. "Dieter" is the first name of a quite popular German musician, who is either loved or hated for his kind of acting and thats exactly what this movie is about. It is based on the autobiography "Dieter Bohlen" wrote a few years ago but isn\'t meant to be accurate on that. The movie is filled with some sexual offensive content (at least for American standard) which is either amusing (not for the other "actors" of course) or dumb - it depends on your individual kind of humor or on you being a "Bohlen"-Fan or not. Technically speaking there isn\'t much to criticize. Speaking of me I find this movie to be an OK-movie.',
        "0",
    ],
]
